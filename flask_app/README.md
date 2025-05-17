# Flask Search Application for BM25

Aplikasi web berbasis Flask untuk mencari dokumen menggunakan algoritma BM25. Aplikasi ini menyediakan antarmuka pencarian yang mirip dengan Google untuk memudahkan pengguna dalam mencari informasi.

## Fitur

- Antarmuka pencarian yang mirip dengan Google
- Menampilkan hasil pencarian dengan judul, link, cuplikan konten, dan skor BM25
- Menggunakan algoritma BM25 untuk meranking hasil pencarian
- Preprocessing teks otomatis (case folding, cleaning, tokenizing, stopword removal)

## Cara Menjalankan Aplikasi

1. Install dependensi yang diperlukan:

   ```
   pip install -r flask_app/requirements.txt
   ```

2. Jalankan aplikasi Flask:

   ```
   cd flask_app
   python app.py
   ```

3. Buka browser dan akses:
   ```
   http://127.0.0.1:5000/
   ```

## Struktur Project

- `app.py`: File utama aplikasi Flask
- `static/`: Folder untuk file statis (CSS, JavaScript, gambar)
  - `style.css`: File CSS untuk styling halaman
- `templates/`: Folder untuk template HTML
  - `index.html`: Template untuk halaman pencarian (home)
  - `search.html`: Template untuk halaman hasil pencarian

## Catatan

Aplikasi ini menggunakan file data.csv dari folder text/ yang ada di project BM25. Pastikan file tersebut berisi kolom Judul, Content, dan Link.
