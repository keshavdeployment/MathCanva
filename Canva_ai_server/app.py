from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from google import genai
from constant import kprompt

import os
load_dotenv()

GENAI_API_KEY = os.getenv("GENAI_API_KEY")

client = genai.Client(api_key=GENAI_API_KEY)

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io

app = FastAPI(title="Canva AI Server")

# UPLOAD_DIR = Path(__file__).parent / "uploads"
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_DIR = Path("/tmp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _timestamp_name(suffix: str = "png") -> str:
    return f"canvas_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}.{suffix}"


def generate_image_output(file_path: str, prompt: str = "Caption this image."):
    my_file = client.files.upload(file=file_path)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[my_file, kprompt],
    )
    print("Generation response:", response)
    return response.text

@app.get("/")
async def root():
    return {"message": "Canva AI Server is running."}


@app.post("/upload")
async def upload_image(
    request: Request,
    file: Optional[UploadFile] = File(default=None),
):
    try:
        # Case 1: multipart form-data with a file field
        if file is not None:
            contents = await file.read()
            suffix = (file.filename.split(".")[-1].lower() if file.filename else "png")
            name = f"output.{suffix}"
            out_path = UPLOAD_DIR / name
            with open(out_path, "wb") as f:
                f.write(contents)
            # Generate output using the saved image and print to terminal
            result_text = None
            try:
                result_text = generate_image_output(str(out_path))
                print(f"[Gemini] {result_text}")
            except Exception as e:
                print(f"[Gemini error] {e}")
            return JSONResponse({"status": "ok", "path": str(out_path.name), "result": result_text})

        # Case 2: raw body (e.g., image/png)
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="No file or body provided")

        # Validate it is an image by attempting to open via PIL
        try:
            img = Image.open(io.BytesIO(body))
            suffix = img.format.lower() if img.format else "png"
        except Exception:
            # Fallback: save as png if not identifiable by PIL
            suffix = "png"

        name = f"output.{suffix}"
        out_path = UPLOAD_DIR / name
        with open(out_path, "wb") as f:
            f.write(body)

        # Generate output using the saved image and print to terminal
        result_text = None
        try:
            result_text = generate_image_output(str(out_path))
            print(f"[Gemini] {result_text}")
        except Exception as e:
            print(f"[Gemini error] {e}")

        return JSONResponse({"status": "ok", "path": str(out_path.name), "result": result_text})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 