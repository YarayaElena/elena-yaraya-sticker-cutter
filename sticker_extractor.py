<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Елена Ярая — Стикеры</title>
    <style>
        body {
            font-family: sans-serif;
            background: #0f0f0f;
            color: white;
            text-align: center;
            margin: 0;
            padding: 0;
        }
        header {
            background: #111;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        header img {
            width: 40px;
            margin-right: 10px;
        }
        h1 { margin: 0; font-size: 1.5em; }
        .upload-box {
            margin: 20px auto;
            padding: 20px;
            border: 2px dashed #555;
            width: 90%;
            max-width: 400px;
            background-color: #1a1a1a;
            border-radius: 10px;
        }
        input[type="file"] { margin: 10px 0; color: white; }
        button {
            padding: 10px 20px;
            background: #FFCF53;
            color: black;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin: 5px;
        }
        #gallery a {
            display: inline-block;
            margin: 10px;
        }
        #gallery img {
            width: 150px;
            border-radius: 12px;
            background: #fff;
            display: block;
        }
        #status { margin-top: 10px; }
    </style>
</head>
<body>
    <header>
        <img src="/static/logo.png" alt="Логотип">
        <h1>Елена Ярая</h1>
    </header>
    <p style="color:#FFCF53; margin: 10px 0;">Обработка стикеров</p>

    <div class="upload-box">
        <input type="file" id="imageInput" accept="image/*"><br>
        <button onclick="uploadImage()" id="uploadBtn">Разрезать стикеры</button>
        <p id="status"></p>
    </div>

    <div id="gallery"></div>

    <script>
        async function uploadImage() {
            const input = document.getElementById('imageInput');
            const btn = document.getElementById('uploadBtn');
            const status = document.getElementById('status');
            const gallery = document.getElementById('gallery');

            if (!input.files.length) {
                alert('Выбери изображение!');
                return;
            }
            const form = new FormData();
            form.append('file', input.files[0]);

            btn.disabled = true;
            status.textContent = 'Обработка...';
            gallery.innerHTML = '';

            try {
                const res = await fetch('/upload', { method: 'POST', body: form });
                const json = await res.json();
                if (!json.files) throw new Error('Нет файлов');

                json.files.forEach(filename => {
                    const link = document.createElement('a');
                    link.href = `/static/output/${filename}`;
                    link.download = filename;
                    const img = document.createElement('img');
                    img.src = `/static/output/${filename}`;
                    img.alt = filename;
                    link.appendChild(img);
                    gallery.appendChild(link);
                });
                status.textContent = 'Готово! Нажми на стикер, чтобы скачать.';
            } catch (err) {
                status.textContent = 'Ошибка: ' + err.message;
            }
            btn.disabled = false;
        }
    </script>
</body>
</html>