import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from starlette.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from faster_whisper_service import FasterWhisperService


app = FastAPI()
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

fws = FasterWhisperService()

class TaskStartReq(BaseModel):
    audio_file_name: str
    language: Optional[str] = None


@app.get("/", include_in_schema=False)
async def root_redirect():
    print("root_redirect")
    return RedirectResponse(url="/static/index.html")

@app.post("/faster-whisper/task/start")
async def start_task(request: TaskStartReq):
    result = fws.transcribe(request.audio_file_name)
    return {"subtitle_file_name": result}

@app.post("/faster-whisper/file/upload")
async def upload_file(file: UploadFile):
    filename = fws.upload_file(file)
    return {"file_name": filename}

@app.get("/faster-whisper/file/download/{filename}", response_class=FileResponse)
async def download_file(filename: str):
    file_path = f"/tmp/output/{filename}"
    return FileResponse(file_path, filename=filename, media_type="application/octet-stream")

@app.on_event("startup")
async def startup_event():
    await background_task()

async def background_task():
    fws.load_model()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8321, reload=True, log_level="info")
