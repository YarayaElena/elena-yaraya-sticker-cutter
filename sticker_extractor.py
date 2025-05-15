from pathlib import Path
from PIL import Image
import cv2
import numpy as np

def extract_stickers(input_path, output_dir, padding=20):
    """
    Разрезает изображение на отдельные стикеры:
    - Сегментирует каждый контур и создаёт маску alpha, чтобы убрать фон и соседние обрезки.
    - Помещает вырезанный sticker в центр прозрачного холста с отступом padding.
    Возвращает список путей к PNG-файлам.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Загрузка изображения с учётом альфа
    img = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Не удалось загрузить изображение")
    h_img, w_img = img.shape[:2]

    # Готовим BGR-изображение и маску alpha
    if img.shape[2] == 4:
        b, g, r, a = cv2.split(img)
        mask = a
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    else:
        img_bgr = img
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Чистим маску от шума
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Находим контуры
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for idx, cnt in enumerate(contours, start=1):
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h < 1000:
            continue

        # Вырезаем ROI и соответствующую маску
        mask_roi = mask[y:y+h, x:x+w]
        roi_bgr = img_bgr[y:y+h, x:x+w]

        # Создаём BGRA из BGR + alpha mask
        b_ch, g_ch, r_ch = cv2.split(roi_bgr)
        alpha_ch = mask_roi
        bgra = cv2.merge((b_ch, g_ch, r_ch, alpha_ch))
        pil_img = Image.fromarray(bgra)

        # Создаём прозрачный холст с padding
        frame_w, frame_h = w + padding*2, h + padding*2
        canvas = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
        canvas.paste(pil_img, (padding, padding), pil_img)

        # Сохраняем
        out_path = output_dir / f"sticker_{idx}.png"
        pil_img.save(out_path)
        results.append(str(out_path))

    return results