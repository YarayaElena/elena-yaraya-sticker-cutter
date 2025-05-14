```python
import cv2
from PIL import Image
import os

def extract_stickers(input_path, output_dir):
    """
    Разрезает изображение с несколькими наклейками по прозрачному фону (alpha channel).
    Сохраняет каждый стикер как PNG в output_dir и возвращает список путей.
    """
    # Убедимся, что выходная папка существует
    os.makedirs(output_dir, exist_ok=True)

    # Загрузка изображения с альфа-каналом
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Не удалось загрузить изображение")

    # Определяем маску: если есть alpha, используем его, иначе threshold на яркость
    if img.shape[2] == 4:
        # каналы B G R A
        b, g, r, a = cv2.split(img)
        mask = a  # маска по непрозрачности
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Находим контуры по маске
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for i, cnt in enumerate(contours, start=1):
        x, y, w, h = cv2.boundingRect(cnt)
        # отфильтруем очень мелкие фрагменты
        if w * h < 1000:
            continue
        crop = img[y:y+h, x:x+w]

        # Конвертируем обрезок в PIL Image (RGBA)
        if crop.shape[2] == 4:
            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGRA2RGBA))
        else:
            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGBA))

        out_path = os.path.join(output_dir, f"sticker_{i}.png")
        pil_img.save(out_path)
        results.append(out_path)

    return results
```