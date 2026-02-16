#!/usr/bin/env python3
"""Merge Whisper transcript segments with diarization segments.

Expectations:
- Whisper JSON: a dict with a "segments" list (each with start, end, text). This is the output of `whisper.Model.transcribe(..., word_timestamps=False)` which by default includes `segments`.
- Diarization JSON: a list of objects [{"start": float, "end": float, "speaker": str}, ...]

The script assigns each whisper segment to the speaker with the largest time overlap.

Example:
  python scripts/merge_transcript_diarization.py \
    --whisper whisper_result.json \
    --diarization diarization.json \
    --format text \
    --out merged.txt

"""
from __future__ import annotations

import argparse
import json
import math
import re
from typing import List, Dict, Any, Optional, Tuple


def load_whisper_segments(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "segments" in data and isinstance(data["segments"], list):
        return data["segments"]

    # If the file looks like a plain transcript, create a single segment
    if isinstance(data, str):
        return [{"start": 0.0, "end": 0.0, "text": data}]

    raise ValueError("Invalid whisper JSON: expected dict with 'segments' list")


def load_diarization_segments(path: str) -> List[Dict[str, Any]]:
    # Try JSON first
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            # Expect list of {start,end,speaker}
            return [
                {"start": float(item["start"]), "end": float(item["end"]), "speaker": str(item["speaker"])}
                for item in data
            ]
    except Exception:
        pass

    # Fallback: parse lines like "[  0.00 \u2192   2.50]  speaker1"
    segs: List[Dict[str, Any]] = []
    pattern = re.compile(r"\[\s*([0-9.]+)\s*\x2192\s*([0-9.]+)\]\s*(.+)")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = pattern.search(line)
            if m:
                start = float(m.group(1))
                end = float(m.group(2))
                speaker = m.group(3).strip()
                segs.append({"start": start, "end": end, "speaker": speaker})

    if segs:
        return segs

    raise ValueError("Could not parse diarization file: supply JSON list or formatted text")


def overlap(a1: float, a2: float, b1: float, b2: float) -> float:
    return max(0.0, min(a2, b2) - max(a1, b1))


def merge_segments(
    whisper_segs: List[Dict[str, Any]], diar_segs: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []

    for w in whisper_segs:
        wstart = float(w.get("start", 0.0))
        wend = float(w.get("end", wstart))
        text = str(w.get("text", "")).strip()

        # Tally overlap per speaker
        per_speaker: Dict[str, float] = {}
        for d in diar_segs:
            s = float(d.get("start", 0.0))
            e = float(d.get("end", 0.0))
            spk = str(d.get("speaker", "unknown"))
            ov = overlap(wstart, wend, s, e)
            if ov > 0:
                per_speaker[spk] = per_speaker.get(spk, 0.0) + ov

        if per_speaker:
            # choose speaker with largest overlap
            speaker = max(per_speaker.items(), key=lambda kv: kv[1])[0]
        else:
            speaker = "(Unknown)"

        merged.append({"start": wstart, "end": wend, "speaker": speaker, "text": text})

    return merged


def format_text(merged: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for m in merged:
        lines.append(f"[{m['start']:7.2f} \u2192 {m['end']:7.2f}]  {m['speaker']}: {m['text']}")
    return "\n".join(lines)


def format_srt(merged: List[Dict[str, Any]]) -> str:
    def to_srt_time(t: float) -> str:
        hours = int(t // 3600)
        minutes = int((t % 3600) // 60)
        seconds = int(t % 60)
        millis = int(round((t - math.floor(t)) * 1000))
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

    parts: List[str] = []
    for i, m in enumerate(merged, start=1):
        parts.append(str(i))
        parts.append(f"{to_srt_time(m['start'])} --> {to_srt_time(m['end'])}")
        parts.append(f"{m['speaker']}: {m['text']}")
        parts.append("")
    return "\n".join(parts)


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Merge Whisper transcript segments with diarization segments")
    p.add_argument("--whisper", required=True, help="Path to whisper JSON result (must contain 'segments')")
    p.add_argument("--diarization", required=True, help="Path to diarization JSON or formatted text")
    p.add_argument("--format", choices=["text", "srt", "json"], default="text", help="Output format")
    p.add_argument("--out", help="Output file (defaults to stdout)")
    args = p.parse_args(argv)

    try:
        whisper_segs = load_whisper_segments(args.whisper)
    except Exception as exc:
        print(f"Error loading whisper segments: {exc}")
        return 2

    try:
        diar_segs = load_diarization_segments(args.diarization)
    except Exception as exc:
        print(f"Error loading diarization segments: {exc}")
        return 3

    merged = merge_segments(whisper_segs, diar_segs)

    if args.format == "text":
        out = format_text(merged)
    elif args.format == "srt":
        out = format_srt(merged)
    else:
        out = json.dumps(merged, indent=2, ensure_ascii=False)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Wrote {args.out}")
    else:
        print(out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
