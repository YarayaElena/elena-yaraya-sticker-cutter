from pathlib import Path
from PIL import Image
import cv2

def extract_stickers(input_path, output_dir, padding_ratio=0.1, min_padding=20):
    """
    Разрезает изображение на стикеры, добавляя отступы вокруг каждого контура,
    чтобы полностью захватить края. Отступ рассчитывается как max(padding_ratio*размер, min_padding).
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Загружаем изображение (с учётом alpha, если есть)
    img = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Не удалось загрузить изображение")
    h_img, w_img = img.shape[:2]

    # Маска по alpha или бинаризации
    if img.shape[2] == 4:
        _, _, _, alpha = cv2.split(img)
        mask = alpha
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Морфологическая обработка для чистоты маски
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Поиск внешних контуров
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for idx, cnt in enumerate(contours, start=1):
        x, y, w, h = cv2.boundingRect(cnt)
        # Фильтрация по минимальной площади
        if w * h < 1000:
            continue

        # Рассчитываем отступы
        pad_w = max(int(w * padding_ratio), min_padding)
        pad_h = max(int(h * padding_ratio), min_padding)
        x1 = max(x - pad_w, 0)
        y1 = max(y - pad_h, 0)
        x2 = min(x + w + pad_w, w_img)
        y2 = min(y + h + pad_h, h_img)

        # Выкладываем обрезанный участок
        crop = img[y1:y2, x1:x2]

        # Преобразуем в PIL RGBA
        if crop.shape[2] == 4:
            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGRA2RGBA))
        else:
            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGBA))

        out_path = output_dir / f"sticker_{idx}.png"
        pil_img.save(out_path)
        results.append(str(out_path))

    return results