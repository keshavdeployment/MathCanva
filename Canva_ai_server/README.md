# Canva AI Server (FastAPI)

## Setup (macOS/Linux)

```bash
cd Canva_ai_server
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## Run

```bash
uvicorn app:app --host 0.0.0.0 --port 3000 --reload
```

Uploads are saved to the `uploads/` folder with timestamped filenames.

## API

- POST `/upload`
  - Accepts either:
    - Raw image bytes (e.g., `Content-Type: image/png`)
    - Multipart form-data with field `file`
  - Returns JSON: `{ "status": "ok", "path": "canvas_YYYYmmdd_HHMMSS_xxxxxx.png" }` 