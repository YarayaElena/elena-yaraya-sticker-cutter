from pathlib import Path
from PIL import Image
import cv2


def extract_stickers(input_path, output_dir):
    """
    Разрезает изображение с несколькими наклейками, объединяя разорванные части.
    Сохраняет каждый стикер как PNG в output_dir и возвращает список путей.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Загрузка изображения
    img = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Не удалось загрузить изображение")

    # Создание маски по альфа или порогу
    if img.shape[2] == 4:
        _, _, _, alpha = cv2.split(img)
        mask = alpha
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Укрупнение и объединение фрагментов: dilate + close
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50))
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.erode(mask, kernel, iterations=1)

    # Нахождение контуров
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for idx, cnt in enumerate(contours, start=1):
        x, y, w, h = cv2.boundingRect(cnt)
        # Отфильтруем слишком мелкие области
        if w * h < 5000:
            continue
        crop = img[y:y+h, x:x+w]

        # Конвертация в RGBA
        if crop.shape[2] == 4:
            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGRA2RGBA))
        else:
            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGBA))

        output_path = output_dir / f"sticker_{idx}.png"
        pil_img.save(output_path)
        results.append(str(output_path))

    return results