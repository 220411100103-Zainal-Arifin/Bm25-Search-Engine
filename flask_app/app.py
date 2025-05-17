"""
BM25 Search Engine - Web Application with Flask

File ini merupakan implementasi web untuk algoritma BM25 menggunakan Flask framework.
Aplikasi web ini menyediakan antarmuka pencarian yang interaktif dan user-friendly
untuk pencarian dokumen menggunakan algoritma BM25.
"""

import os
import sys

# MODIFIKASI: Mengimpor modul Flask untuk web application
# Flask digunakan sebagai framework web untuk menyediakan antarmuka pencarian
from flask import Flask, request, render_template
# MODIFIKASI: Mengimpor parser dari modul src untuk pemrosesan corpus dan query
# CorpusParser digunakan untuk memproses dataset dokumen
# QueryParser digunakan untuk memproses query pengguna
from src.parse import CorpusParser, QueryParser
# MODIFIKASI: Mengimpor QueryProcessor untuk menjalankan algoritma BM25
# QueryProcessor menjalankan algoritma BM25 untuk mendapatkan hasil pencarian yang relevan
from src.query import QueryProcessor

# MODIFIKASI: Inisialisasi aplikasi Flask
# Membuat instance Flask untuk menangani routing dan HTTP requests
app = Flask(__name__)

# MODIFIKASI: Menggunakan path relatif untuk file data
# Path relatif memungkinkan aplikasi berjalan di berbagai lingkungan
# Dengan menggunakan os.path.join dan __file__, aplikasi dapat berjalan 
# dari direktori mana pun tanpa perlu mengubah kode
data_path = os.path.join(os.path.dirname(__file__), 'text', 'data.csv')

# MODIFIKASI: Inisialisasi corpus di awal aplikasi untuk performa yang lebih baik
# Memproses corpus hanya sekali saat startup, bukan setiap kali ada request
# Hal ini meningkatkan responsivitas aplikasi karena tidak perlu parsing ulang
# Teknik ini dikenal sebagai "lazy loading" atau "precomputation" yang umum 
# digunakan dalam aplikasi web untuk mempercepat respons request
cp = CorpusParser(filename=data_path)
cp.parse()  # Melakukan preprocessing dan indexing corpus
corpus = cp.get_corpus()  # Mendapatkan korpus terpreprocessed untuk BM25
full_corpus = cp.get_full_corpus()  # Mendapatkan korpus dengan metadata untuk tampilan hasil

@app.route('/', methods=['GET'])
def home():
    """Halaman utama dengan form pencarian
    
    MODIFIKASI: Menggunakan routing Flask untuk endpoint utama
    Menampilkan halaman awal dengan form pencarian yang user-friendly
    Menggunakan template HTML untuk rendering halaman
    
    Returns:
        HTML: Halaman utama dengan form pencarian yang dirender dari template index.html
    """
    # MODIFIKASI: Menggunakan template engine Flask untuk merender HTML
    # Template engine memungkinkan pemisahan antara logika aplikasi dan tampilan
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    """Halaman hasil pencarian
    
    MODIFIKASI: Implementasi endpoint untuk memproses dan menampilkan hasil pencarian
    Menerima parameter query dari GET request dan memproses menggunakan BM25
    Menampilkan hasil pencarian dengan metadata lengkap dalam format yang terstruktur
    
    Endpoint ini melakukan beberapa tahap:
    1. Mendapatkan query dari parameter URL
    2. Memproses query menggunakan algoritma BM25
    3. Mengambil metadata dokumen yang relevan
    4. Memformat hasil pencarian untuk ditampilkan
    
    Returns:
        HTML: Halaman hasil pencarian dengan daftar dokumen yang relevan
              atau halaman utama jika query kosong
    """
    # MODIFIKASI: Mendapatkan query dari parameter URL
    # Parameter q digunakan sebagai kata kunci pencarian
    query_text = request.args.get('q', '')
    
    # MODIFIKASI: Redirect ke halaman utama jika query kosong
    # Menghindari pencarian dengan query kosong yang tidak bermakna
    if not query_text:
        return render_template('index.html')
      # MODIFIKASI: Proses query menggunakan algoritma BM25
    # Menggunakan implementasi yang sama dengan versi command line untuk konsistensi hasil
    # Fase 1: Parse query - memproses query pengguna menggunakan QueryParser
    qp = QueryParser(query=query_text)
    qp.parse()  # Melakukan preprocessing pada query (lowercase, hapus tanda baca, stopwords)
    queries = qp.get_queries()  # Mendapatkan query yang sudah diproses
    
    # Fase 2: Jalankan pencarian - menggunakan QueryProcessor untuk menghitung skor BM25
    proc = QueryProcessor(queries, corpus)
    results = proc.run()  # Menjalankan algoritma BM25 untuk mendapatkan peringkat dokumen
    
    # MODIFIKASI: Inisialisasi list untuk menyimpan hasil pencarian yang terformat
    # Hasil akan berisi metadata dokumen yang relevan untuk ditampilkan ke pengguna
    search_results = []
    if results:
        for result in results:
            # MODIFIKASI: Mengurutkan hasil berdasarkan skor BM25 (dari tinggi ke rendah)
            # Sorting penting untuk menampilkan dokumen paling relevan terlebih dahulu
            sorted_results = sorted(result.items(), key=lambda x: x[1], reverse=True)            
            
            # MODIFIKASI: Membatasi hasil pencarian hanya 20 dokumen teratas
            # Pembatasan ini untuk keterbacaan dan performa halaman
            for doc_id, score in sorted_results[:20]:
                # MODIFIKASI: Mengambil metadata dokumen dari corpus lengkap
                # Metadata digunakan untuk menampilkan informasi lengkap ke pengguna
                doc_data = full_corpus[doc_id]
                title = doc_data['title']  # Judul dokumen
                link = doc_data['link']    # Link ke dokumen asli
                content = doc_data['content']  # Konten dokumen
                
                # MODIFIKASI: Membuat cuplikan konten (snippet) untuk tampilan hasil
                # Snippet membantu pengguna memahami konteks dokumen tanpa perlu membaca seluruhnya
                snippet = content[:200] + "..." if len(content) > 200 else content                
                
                # MODIFIKASI: Menyimpan hasil dalam format terstruktur untuk template
                # Format terstruktur memudahkan rendering di template HTML
                search_results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'score': score  # Skor BM25 menunjukkan tingkat relevansi dokumen
                })
      # MODIFIKASI: Render template hasil pencarian dengan data query dan hasil
    # Template search.html akan menampilkan hasil pencarian dalam format yang mudah dibaca
    # Parameter query dan results akan tersedia dalam template untuk digunakan
    return render_template('search.html', query=query_text, results=search_results)

# MODIFIKASI: Conditional untuk menjalankan aplikasi secara langsung
if __name__ == '__main__':
    # MODIFIKASI: Menjalankan aplikasi dengan mode debug aktif
    # Mode debug memudahkan pengembangan dengan fitur auto-reload dan error traceback
    app.run(debug=True)
