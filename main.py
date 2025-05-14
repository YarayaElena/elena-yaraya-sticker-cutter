from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import shutil
import uuid
from sticker_extractor import extract_stickers

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    uid = str(uuid.uuid4())
    temp_folder = f"temp/{uid}"
    os.makedirs(temp_folder, exist_ok=True)
    input_path = os.path.join(temp_folder, "input.png")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    zip_path = extract_stickers(input_path, temp_folder)
    return FileResponse(zip_path, filename="stickers.zip", media_type="application/zip")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
