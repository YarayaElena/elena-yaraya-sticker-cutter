from PIL import Image
import cv2
import numpy as np

def extract_stickers(input_path, output_dir):
    input_path = str(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Загружаем изображение
    image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError("Не удалось загрузить изображение")

    # Грейскейл + бинаризация
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Поиск контуров
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []

    for i, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)

        if w < 50 or h < 50:  # Пропуск слишком мелких
            continue

        crop = image[y:y+h, x:x+w]

        # Преобразуем в PNG с прозрачным фоном
        pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGBA))
        output_path = output_dir / f"sticker_{i+1}.png"
        pil_img.save(output_path)
        results.append(str(output_path))

    return results