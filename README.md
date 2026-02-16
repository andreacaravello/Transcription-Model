# Minimal Transcriber with Diarization

This project provides a simple Gradio-based web interface to:

- Upload an **English** audio file
- Automatically transcribe it using OpenAI Whisper (`small.en` model)
- Run **speaker diarization** using `pyannote.audio`
- Output speaker-tagged transcript and timestamped segments

## Usage

### 1. Build the Docker container
```bash
docker build -t transcriber .
```

### 2. Setup Environment

1. Copy `.env.template` to `.env`:
```bash
cp .env.template .env
```

2. Add your HuggingFace token to `.env`:
```bash
HUGGINGFACE_TOKEN=your_token_here
```

### 3. Run the app
```bash
# Run with .env file (recommended)
docker run --env-file .env -p 7860:7860 transcriber
```

Then open `http://localhost:7860` and upload an audio file.

## Output
- Transcript with speaker labels
- JSON segments with timestamps and speakers
- Downloadable `.txt` and `.srt` files

## Requirements
See `requirements.txt` for pinned versions.

## Notes
- Only **audio uploads** are supported. No YouTube links.
- Language is **fixed to English**.
- Diarization is **always enabled**.
- Whisper model is fixed to `small.en`.

## Quickstart (developer)

Follow these steps for local development and to run the app with docker-compose.

1. Create a Python virtual environment and install dependencies (optional, for local edits):
```bash
python3 -m venv .venv
source .venw/bin/activate
pip install -r requirements.txt
```

2. Create your `.env` from the template and add your Hugging Face token:
```bash
cp .env.template .env
# Edit .env and set HUGGINGFACE_TOKEN =your_token_here
```

3. Start the app using docker-compose (recommended):
```bash
docker compose up -d --build
# Visit http://localhost:7860
```

4. Stop the service:
```bash
docker compose down
```

## Makefile

A `Makefile` is included for convenience. Common targets:

- `make venv` \u2014 create `.venv`
- `make install` \u2014 install Python deps into `.venv`
- `make build` \u2014 build the Docker image
- `make up` \u2014 start via `docker compose up -d --build`
- `make down` \u2014 stop the compose stack
- `make logs` \u2014 follow logs from the service

Example:
```bash
make venv
make install
make up
```

---

MIT License.
