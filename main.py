from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import uuid
from sticker_extractor import extract_stickers

app = FastAPI()

# Указываем путь к static
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    temp_dir = Path("static/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Удаляем старые файлы
    for f in temp_dir.glob("*.png"):
        f.unlink()

    # Сохраняем загруженное изображение
    img_path = temp_dir / f"input_{uuid.uuid4().hex}.png"
    with img_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Вырезаем стикеры
    saved_files = extract_stickers(img_path, temp_dir)

    # Возвращаем список имён файлов
    return JSONResponse({"files": [Path(f).name for f in saved_files]})