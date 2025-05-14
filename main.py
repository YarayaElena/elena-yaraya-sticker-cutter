from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import uuid
from sticker_extractor import extract_stickers

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    temp_dir = Path("static/temp")
    output_dir = Path("static/output")
    temp_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Очищаем папки
    for f in temp_dir.glob("*.png"):
        f.unlink()
    for f in output_dir.glob("*.png"):
        f.unlink()

    # Сохраняем загруженный файл
    img_path = temp_dir / f"input_{uuid.uuid4().hex}.png"
    with img_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Разрезаем стикеры
    stickers = extract_stickers(img_path, temp_dir)

    # Копируем в output
    result_files = []
    for src in stickers:
        dest = output_dir / Path(src).name
        shutil.copy(src, dest)
        result_files.append(dest.name)

    return JSONResponse({"files": result_files})

@app.get("/download-all")
def download_all():
    output_dir = Path("static/output")
    zip_path = output_dir / "stickers.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for png in output_dir.glob("*.png"):
            zipf.write(png, arcname=png.name)

    return FileResponse(zip_path, filename="stickers.zip")