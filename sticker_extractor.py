from pathlib import Path
from PIL import Image
import cv2

def extract_stickers(input_path, output_dir, padding=20):
    """
    Разрезает изображение на отдельные стикеры,
    создаёт для каждого прозрачный холст с отступами
    и сохраняет в output_dir.
    Возвращает список путей к PNG-файлам.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Загрузим изображение
    img = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Не удалось загрузить изображение")
    h_img, w_img = img.shape[:2]

    # Маска: alpha-канал или бинаризация по яркости
    if img.shape[2] == 4:
        _, _, _, alpha = cv2.split(img)
        mask = alpha
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Очищаем мелкие шумы
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Ищем контуры
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for idx, cnt in enumerate(contours, start=1):
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h < 1000:  # пропускаем слишком маленькие
            continue

        # Вырезаем фрагмент
        crop = img[y:y+h, x:x+w]

        # Конвертируем в PIL Image RGBA
        if crop.shape[2] == 4:
            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGRA2RGBA))
        else:
            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGBA))

        # Создаём прозрачный холст с полями
        frame_w = w + padding * 2
        frame_h = h + padding * 2
        canvas = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
        canvas.paste(pil_img, (padding, padding), pil_img)

        # Сохраняем и собираем пути
        out_path = output_dir / f"sticker_{idx}.png"
        canvas.save(out_path)
        results.append(str(out_path))

    return results