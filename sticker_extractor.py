import cv2
from PIL import Image
import os
import zipfile

def extract_stickers(image_path, output_folder):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Не удалось загрузить изображение")

    # Грейскейл + блюр + Canny
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blur, 30, 120)

    # Морфологическая замтка для объединения фрагментов
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Находим контуры
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Фильтруем по площади (пропустить мелкие детали)
    contours = [c for c in contours if cv2.contourArea(c) > 5000]

    stickers_dir = os.path.join(output_folder, "stickers")
    os.makedirs(stickers_dir, exist_ok=True)

    saved = []
    for i, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        crop = img[y:y+h, x:x+w]

        # Конверт и центрирование в 512×512
        pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGBA))
        final = Image.new("RGBA", (512, 512), (0,0,0,0))
        pil.thumbnail((512, 512), Image.LANCZOS)
        off = ((512 - pil.width)//2, (512 - pil.height)//2)
        final.paste(pil, off, pil)
        
        path = os.path.join(stickers_dir, f"sticker_{i+1}.png")
        final.save(path)
        saved.append(path)

    # Упаковываем в ZIP
    zip_path = os.path.join(output_folder, "stickers.zip")
    with zipfile.ZipFile(zip_path, 'w') as z:
        for p in saved:
            z.write(p, arcname=os.path.basename(p))

    return zip_path