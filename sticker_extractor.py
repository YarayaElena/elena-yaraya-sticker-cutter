```python
from pathlib import Path
from PIL import Image
import cv2

def extract_stickers(input_path, output_dir, padding=20):
    """
    Разрезает изображение на отдельные стикеры, а затем помещает каждый вырезанный
    фрагмент в прозрачный кадр с отступами, чтобы сохранить весь контур без обрезки.
    Возвращает список путей к сохранённым PNG-файлам.
    """
    # Подготовка папки вывода
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Загрузка изображения (с учётом альфа-канала)
    img = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Не удалось загрузить изображение")

    # Создание маски по альфа-каналу или порогу по яркости
    if img.shape[2] == 4:
        _, _, _, alpha = cv2.split(img)
        mask = alpha
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Лёгкая очистка маски от шума
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Поиск контуров
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for idx, cnt in enumerate(contours, start=1):
        x, y, w, h = cv2.boundingRect(cnt)
        # Пропускаем слишком маленькие фрагменты
        if w * h < 1000:
            continue

        # Вырезаем область
        crop = img[y:y+h, x:x+w]

        # Конвертация в PIL Image (RGBA)
        if crop.shape[2] == 4:
            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGRA2RGBA))
        else:
            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGBA))

        # Создаём прозрачный холст с отступами
        frame_w = w + padding * 2
        frame_h = h + padding * 2
        canvas = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
        # Вставляем вырезанный стикер по центру с учетом padding
        canvas.paste(pil_img, (padding, padding), pil_img)

        # Сохраняем файл
        out_path = output_dir / f"sticker_{idx}.png"
        canvas.save(out_path)
        results.append(str(out_path))

    return results
```