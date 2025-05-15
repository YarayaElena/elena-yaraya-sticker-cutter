from pathlib import Path
from PIL import Image
import cv2
import numpy as np

def extract_stickers(input_path, output_dir, padding=20):
    """
    Разрезает исходное изображение на отдельные стикеры:
    1) Сегментирует область каждого контура,
    2) Применяет маску для вырезанного ROI, убирая фон и соседние обрезки,
    3) Вставляет прозрачный вырезанный стикер в холст с отступами (padding),
    4) Сохраняет каждый как PNG и возвращает список путей.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Загружаем изображение (с alpha или без)
    img = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Не удалось загрузить изображение")

    # Разделяем на BGR и маску alpha
    if img.shape[2] == 4:
        b, g, r, a = cv2.split(img)
        img_bgr = cv2.merge((b, g, r))
        mask_full = a
    else:
        img_bgr = img
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        _, mask_full = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Очищаем маску от мелких шумов
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_clean = cv2.morphologyEx(mask_full, cv2.MORPH_OPEN, kernel, iterations=1)

    # Находим контуры каждого объекта
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for idx, cnt in enumerate(contours, start=1):
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h < 1000:  # пропускаем слишком маленькие
            continue

        # Вырезаем ROI и соответствующую маску
        roi_bgr = img_bgr[y:y+h, x:x+w]
        mask_roi = mask_clean[y:y+h, x:x+w]

        # Создаём BGRA: BGR + alpha mask
        b_ch, g_ch, r_ch = cv2.split(roi_bgr)
        bgra = cv2.merge((b_ch, g_ch, r_ch, mask_roi))
        pil_roi = Image.fromarray(cv2.cvtColor(bgra, cv2.COLOR_BGRA2RGBA))

        # Создаём прозрачный холст с padding
        canvas_w = w + padding * 2
        canvas_h = h + padding * 2
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        canvas.paste(pil_roi, (padding, padding), pil_roi)

        # Сохраняем на диск
        out_path = output_dir / f"sticker_{idx}.png"
        canvas.save(out_path)
        results.append(str(out_path))

    return results