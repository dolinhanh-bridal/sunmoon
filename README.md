# SunMoon Art & Education — website

Một trang, 3 ngôn ngữ (VI / EN / 中文). KHÔNG sửa tay `index.html`.

- Sửa nội dung: `src/body-vi.html`, `src/body-en.html`, `src/body-zh.html`
- Sửa giao diện: `src/head.html`
- Đổi ảnh: chép ảnh vào `assets/photos/`, khai báo trong `src/photos.json`
- Dựng lại: `python3 build.py` (cho hosting) hoặc `python3 build.py --inline` (bản nhúng ảnh)
