import os
import warnings
from typing import List, Tuple, Optional, Dict, Any

import gradio as gr
from fastapi import FastAPI
import importlib
import logging

# Lightweight dependency import checker. This tries to import the requested
# packages and returns a serializable status map. We avoid heavy initialization
# (no model downloads) \u2014 this is only to surface missing packages / import errors
# early and give clear messages in logs and the /health endpoint.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def check_dependencies() -> dict:
    """Attempt to import key runtime packages and return status info.

    Returns a dict of package -> {ok: bool, error: str | None}.
    """
    pkgs = [("gradio", "gradio"), ("fastapi", "fastapi"), ("whisper", "whisper"), ("pyannote.audio", "pyannote.audio")]
    status = {}
    for name, mod in pkgs:
        try:
            importlib.import_module(mod)
            status[name] = {"ok": True, "error": None}
        except Exception as exc:
            status[name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return status

# -----------------------------
# 1) Gradio schema crash guard
#    (fixes "argument of type 'bool' is not iterable")
# -----------------------------
try:
    from gradio_client import utils as _gc_utils  # type: ignore
    _orig__json_to_py = _gc_utils._json_schema_to_python_type

    def _safe_json_schema_to_python_type(schema, defs=None):
        # Some versions emit `True`/`False` instead of an object in additionalProperties, etc.
        if isinstance(schema, bool):
            return "any"
        return _orig__json_to_py(schema, defs)

    _gc_utils._json_schema_to_python_type = _safe_json_schema_to_python_type  # type: ignore
    _gc_utils.json_schema_to_python_type = _safe_json_schema_to_python_type   # type: ignore
except Exception:
    # If the import ever changes upstream, just carry on; the app still runs.
    pass


# -----------------------------
# 2) Lazy loaders (reduce startup RAM)
# -----------------------------
def _load_whisper(model_name: str = "base"):
    import whisper
    return whisper.load_model(model_name)


def _load_diarization_pipeline():
    # Requires a valid Hugging Face token with access to pyannote pipelines
    from pyannote.audio import Pipeline

    token = os.getenv("HUGGINGFACE_TOKEN", "").strip()
    if not token:
        raise RuntimeError("No HUGGINGFACE_TOKEN found in environment. "
                            "Create a .enw with HUGGINGFACE_TOKEN=hf_xxx and pass it via --env-file .env")

    # Suppress a noisy internal PyTorch / pyannote warning that's benign for short segments
    # (std(): degrees of freedom is <= 0). This spams logs but doesn't indicate a fatal error.
    warnings.filterwarnings(
        "ignore",
        message=r\std\(\): degrees of freedom is <= 0",
        category=UserWarning,
    )

    # Default (speaker diarization) pipeline; adjust to your subscription/model access
    # Example model: "pyannote/speaker-diarization-3.1". Wrap load in a friendly error message
    try:
        return Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
    except Exception as exc:
        # Surface a clear runtime error for the UI/logs instead of a stack trace from deep inside HF libs.
        raise RuntimeError(
            "Failed to load diarization pipeline from Hugging Face. "
            "Ensure your HUGGINGFACE_TOKEN has the correct scopes and the model id is accessible. "
            f"Underlying error: {exc}"
        )


# -----------------------------
# 3) Core logic
# -----------------------------
def _format_diarization(segments) -> str:
    """
    segments: iterable of (start, end, speaker_label)
    """
    lines = []
    for s, e, spk in segments:
        lines.append(f"[{s:7.2f} \u2192 {e:7.2f}]  {spk}")
    return "\n".join(lines) if lines else "(no speaker segments)"


def transcribe_and_diarize(
    audio_path: str,
    whisper_model: str,
    enable_diarization: bool
) -> Tuple[str, str, str]:
    """
    Returns:
      - transcription (str)
      - diarization text (str)
      - combined text (str)
    """
    if not audio_path:
        return "", "No audio provided.", ""

    # --- Transcribe ---
    try:
        model = _load_whisper(whisper_model)
        # 'openai-whisper' expects path; set fp16 to False on CPU
        result = model.transcribe(audio_path, fp16=False)
        text = (result or {}).get("text", "").strip()
    except Exception as exc:
        text = f"\u274c Transcription error: {exc}"
        return text, "", ""

    # --- (Optional) Diarize ---
    diar_text = ""
    combined_text = ""
    if enable_diarization:
        try:
            pipeline = _load_diarization_pipeline()
            diar = pipeline(audio_path)

            # Collect speaker-labeled segments for diarization output
            segs: List[Tuple[float, float, str]] = []
            # Also collect in format for merger
            diar_segs: List[Dict[str, Any]] = []
            
            # diar is an Annotation; iterate over segments and labels
            for (start, end), _, label in diar.itertracks(yield_label=True):
                start_t, end_t = float(start), float(end)
                speaker = str(label)
                segs.append((start_t, end_t, speaker))
                diar_segs.append({"start": start_t, "end": end_t, "speaker": speaker})

            diar_text = _format_diarization(segs)

            # Merge transcript with diarization using our merge script
            from scripts.merge_transcript_diarization import merge_segments, format_text
            
            # Convert whisper result to segments
            whisper_segs = [{"start": s["start"], "end": s["end"], "text": s["text"]} 
                          for s in result.get("segments", [])]
            
            if whisper_segs:
                # Merge and format as text
                merged = merge_segments(whisper_segs, diar_segs)
                combined_text = format_text(merged)
            else:
                combined_text = "(no transcript segments to merge)"

        except Exception as exc:
            diar_text = f"\u26a0\ufe0f Diarization error: {exc}"
            combined_text = f"\u26a0\ufe0f Could not merge: {exc}"
    else:
        diar_text = "(diarization disabled)"
        combined_text = text  # Just use transcript when diarization is off

    return text or "(empty transcript)", diar_text, combined_text


# -----------------------------
# 4) UI (Gradio Blocks)
# -----------------------------
with gr.Blocks(title="Transcribe + Diarize", css="footer {visibility: hidden}") as demo:
    gr.Markdown("# \ud83c\udf99\ufe0f Transcribe + (optional) Diarize")

    with gr.Row():
        audio_input = gr.Audio(label="Audio file (wav/mp3/m4a\u2026)", type="filepath")
    with gr.Row():
        model_dd = gr.Dropdown(
            label="Whisper model",
            choices=["tiny", "base", "small", "medium", "large-v3"],
            value="base"
        )
        diar_ck = gr.Checkbox(label="Enable diarization (requires HUGGINGFACE_TOKEN)", value=False)

    go = gr.Button("Transcribe")

    with gr.Row():
        with gr.Column():
            out_text = gr.Textbox(label="Transcript", lines=8)
            out_diar = gr.Textbox(label="Diarization", lines=8)
        out_combined = gr.Textbox(label="Transcript + Diarization", lines=16)

    # IMPORTANT: pass components (not values) to inputs/outputs
    go.click(
        fn=transcribe_and_diarize,
        inputs=[audio_input, model_dd, diar_ck],
        outputs=[out_text, out_diar, out_combined],
        api_name=None
    )

# -----------------------------
# 5) FastAPI app + mount Gradio
#    Works with: uvicorn app:app --host 0.0.0.0 --port 7860
# ------------------------------
_fastapi = FastAPI()


@_fastapi.get("/health")
def _health():
    """Health endpoint that reports import status for key dependencies.

    This is intentionally lightweight (no model loading) and is useful for
    CI / container health checks.
    """
    deps = check_dependencies()
    overall = all(info["ok"] for info in deps.values())
    return {"ok": overall, "dependencies": deps}


# Log dependency status at startup so it's visible in container logs.
deps_status = check_dependencies()
for pkg, info in deps_status.items():
    if info["ok"]:
        logger.info(f"Dependency OK: {pkg}")
    else:
        logger.warning(f"Dependency MISSING/FAILED: {pkg} -> {info['error']}")

app = gr.mount_gradio_app(_fastapi, demo, path="/")

# If you prefer running `python app.py` locally instead of uvicorn:
if __name__ == "__main__":
    # Note: inside Docker we use uvicorn via CMD; this path is for local dev.
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)