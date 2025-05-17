# BM25 Search Engine - Dokumentasi Lengkap

Dokumen ini berisi penjelasan lengkap tentang implementasi algoritma BM25 untuk mesin pencari teks, termasuk modifikasi yang dilakukan, penjelasan algoritma, dan cara menjalankannya.

## Daftar Isi

1. [Gambaran Umum Modifikasi](#gambaran-umum-modifikasi)
2. [Detail Algoritma BM25](#detail-algoritma-bm25)
3. [Struktur Kode](#struktur-kode)
4. [Alur Proses Pencarian](#alur-proses-pencarian)
5. [Cara Menjalankan Kode](#cara-menjalankan-kode)
6. [Contoh Output](#contoh-output)
7. [Perbandingan dengan Kode Awal](#perbandingan-dengan-kode-awal)
8. [Implementasi Web dengan Flask](#implementasi-web-dengan-flask)

## Gambaran Umum Modifikasi

Berikut adalah daftar perubahan utama yang dilakukan pada kode original:

### 1. Format Input Data

- **Original**: File teks biasa dengan format khusus (`#docid content`)
- **Modifikasi**: Format CSV terstruktur dengan kolom metadata (judul, konten, link)

### 2. Preprocessing Teks

- **Original**: Tidak ada preprocessing khusus
- **Modifikasi**:
  - Case folding (lowercase)
  - Menghapus tanda baca dan angka
  - Tokenisasi
  - Penghapusan stopwords

### 3. Parameter BM25

- **Original**: Parameter `qf`, `r`, dan `R` yang tidak efektif
- **Modifikasi**: Penyederhanaan parameter dan pemisahan fungsi TF dan IDF untuk kejelasan

### 4. Interface Pengguna

- **Original**: Input melalui file dan output berbentuk tabel sederhana
- **Modifikasi**: Input melalui command line dan output yang lebih informatif dengan metadata

### 5. Struktur Data

- **Original**: Hanya menyimpan token dokumen
- **Modifikasi**: Menyimpan metadata dokumen (judul, konten, link) untuk hasil pencarian yang lebih kaya

## Detail Algoritma BM25

### Konsep Dasar BM25

BM25 (Best Matching 25) adalah algoritma ranking untuk information retrieval yang menghitung relevansi dokumen terhadap query. Algoritma ini merupakan pengembangan dari model probabilistik yang memadukan:

1. **Term Frequency (TF)**: Seberapa sering term/kata muncul dalam dokumen
2. **Inverse Document Frequency (IDF)**: Seberapa unik term dalam keseluruhan koleksi dokumen
3. **Normalisasi Panjang Dokumen**: Mengkompensasi dokumen yang panjang agar tidak mendominasi hasil

### Rumus BM25

Rumus BM25 yang diimplementasikan dalam kode:

```
score = IDF × TF_component

dimana:
- IDF = log((N - n + 0.5) / (n + 0.5) + 1)
- TF_component = (TF × (k1 + 1)) / (TF + K)
- K = k1 × (1 - b + b × dl/avdl)
- TF = f / dl
```

Keterangan:

- `N`: Jumlah total dokumen dalam korpus
- `n`: Document frequency (jumlah dokumen yang mengandung term)
- `f`: Raw frequency (jumlah kemunculan term dalam dokumen)
- `dl`: Document length (panjang dokumen)
- `avdl`: Average document length (rata-rata panjang dokumen)
- `k1`: Parameter saturasi frekuensi term (nilai = 1.2)
- `b`: Parameter normalisasi panjang dokumen (nilai = 0.75)

### Penjelasan Parameter BM25

#### k1 (Term Frequency Saturation)

- **Nilai Default**: 1.2
- **Fungsi**: Mengontrol seberapa cepat pengaruh frekuensi term mencapai saturasi
- **Efek**:
  - Nilai lebih tinggi: Frekuensi kata lebih berpengaruh (penghargaan pada frekuensi tinggi)
  - Nilai lebih rendah: Efek frekuensi cepat mencapai saturasi (diminishing returns)
  - k1 = 0: Binary model, hanya keberadaan term yang dihitung, bukan frekuensi

#### b (Document Length Normalization)

- **Nilai Default**: 0.75
- **Fungsi**: Mengontrol seberapa kuat normalisasi panjang dokumen
- **Efek**:
  - b = 1: Normalisasi panjang dokumen penuh (dokumen pendek lebih diutamakan)
  - b = 0: Tidak ada normalisasi (panjang dokumen tidak berpengaruh)
  - b = 0.75: Normalisasi sebagian (nilai standar yang memberikan keseimbangan)

### Perhitungan BM25 Step-by-step

Untuk setiap term dalam query, BM25 menghitung:

1. **Term Frequency (TF)**:

   ```python
   # MODIFIKASI: Menambahkan fungsi untuk menghitung Term Frequency
   def calculate_tf(raw_count, total_words):
       """
       Hitung Term Frequency sesuai rumus: TF(t,D) = Raw Count / Total Words in D

       Args:
           raw_count: Jumlah kemunculan term dalam dokumen
           total_words: Total kata dalam dokumen

       Returns:
           Term Frequency
       """
       return raw_count / total_words if total_words > 0 else 0
   ```

   - Mengukur kepadatan term dalam dokumen
   - Nilai tinggi: Term sering muncul relatif terhadap panjang dokumen

2. **Inverse Document Frequency (IDF)**:

   ```python
   # MODIFIKASI: Menambahkan fungsi untuk menghitung Inverse Document Frequency
   def calculate_idf(N, DF):
       """
       Hitung Inverse Document Frequency sesuai rumus:
       IDF = ln((N - DF + 0.5) / (DF + 0.5) + 1)

       Args:
           N: Jumlah total dokumen dalam corpus
           DF: Document frequency (jumlah dokumen yang mengandung term)

       Returns:
           Inverse Document Frequency
       """
       return log((N - DF + 0.5) / (DF + 0.5) + 1)
   ```

   - Mengukur keunikan term dalam koleksi
   - Nilai tinggi: Term jarang ditemukan dalam koleksi dokumen
   - Penambahan +1 memastikan IDF selalu positif

3. **Faktor Normalisasi Panjang (K)**:

   ```python
   def compute_K(dl, avdl):
       """
       Hitung faktor normalisasi panjang dokumen
       """
       return k1 * ((1-b) + b * (float(dl)/float(avdl)))
   ```

   - Menyesuaikan skor berdasarkan perbandingan panjang dokumen dengan rata-rata
   - K lebih kecil untuk dokumen pendek, lebih besar untuk dokumen panjang

4. **Komponen TF dengan Saturasi**:

   ```python
   # MODIFIKASI: Merevisi fungsi score_BM25 untuk lebih jelas dan dengan parameter yang disederhanakan
   def score_BM25(n, f, N, dl, avdl):
       """
       Hitung skor BM25 sesuai rumus:
       BM25(Q,D) = ∑ IDF(t) × (TF(t,D) × (k1 + 1)) / (TF(t,D) + k1 × (1 - b + b × |D|/avgD))

       Args:
           n: Document frequency (jumlah dokumen yang mengandung term)
           f: Raw frequency (jumlah kemunculan term dalam dokumen)
           N: Jumlah total dokumen
           dl: Document length (panjang dokumen)
           avdl: Average document length (rata-rata panjang dokumen)

       Returns:
           Skor BM25
       """
       # Hitung term frequency
       tf = calculate_tf(f, dl)

       # Hitung inverse document frequency
       idf = calculate_idf(N, n)

       # Hitung faktor normalisasi panjang dokumen
       K = compute_K(dl, avdl)

       # MODIFIKASI: Mengimplementasi rumus BM25 dengan lebih jelas
       tf_component = (tf * (k1 + 1)) / (tf + K)

       return idf * tf_component
   ```

   - Menerapkan saturasi pada frekuensi term
   - Mencegah dokumen dengan banyak pengulangan term mendominasi hasil

5. **Skor Final**:
   ```python
   score = idf * tf_component
   ```
   - Mengalikan faktor uniqueness (IDF) dengan faktor kemunculan (TF)
   - Skor tinggi: Term unik yang sering muncul dalam dokumen

## Struktur Kode

Berikut adalah penjelasan komprehensif tentang struktur kode dalam sistem pencarian BM25:

### 1. `invdx.py` - Inverted Index

File ini berfungsi untuk membangun dan mengelola inverted index serta informasi panjang dokumen. Inverted index adalah struktur data kunci dalam sistem pencarian yang memungkinkan akses cepat ke dokumen berdasarkan term.

```python
class InvertedIndex:

    def __init__(self):
        self.index = dict()

    def __contains__(self, item):
        return item in self.index

    def __getitem__(self, item):
        return self.index[item]

    def add(self, word, docid):
        if word in self.index:
            if docid in self.index[word]:
                self.index[word][docid] += 1
            else:
                self.index[word][docid] = 1
        else:
            d = dict()
            d[docid] = 1
            self.index[word] = d

    #frequency of word in document
    def get_document_frequency(self, word, docid):
        if word in self.index:
            if docid in self.index[word]:
                return self.index[word][docid]
            else:
                raise LookupError('%s not in document %s' % (str(word), str(docid)))
        else:
            raise LookupError('%s not in index' % str(word))

    #frequency of word in index, i.e. number of documents that contain word
    def get_index_frequency(self, word):
        if word in self.index:
            return len(self.index[word])
        else:
            raise LookupError('%s not in index' % word)


class DocumentLengthTable:

    def __init__(self):
        self.table = dict()

    def __len__(self):
        return len(self.table)

    def add(self, docid, length):
        self.table[docid] = length

    def get_length(self, docid):
        if docid in self.table:
            return self.table[docid]
        else:
            raise LookupError('%s not found in table' % str(docid))

    def get_average_length(self):
        sum = 0
        for length in self.table.values():
            sum += length
        return float(sum) / float(len(self.table))


def build_data_structures(corpus):
    idx = InvertedIndex()
    dlt = DocumentLengthTable()
    for docid in corpus:

        #build inverted index
        for word in corpus[docid]:
            idx.add(str(word), str(docid))

        #build document length table
        length = len(corpus[str(docid)])
        dlt.add(docid, length)
    return idx, dlt
```

**Detail Implementasi:**

- **InvertedIndex**: Kelas yang menyimpan pemetaan term → dokumen → frekuensi
  - Menyediakan metode untuk menambahkan term baru ke indeks
  - Menghitung frekuensi dokumen dan frekuensi indeks untuk term tertentu
  - Menggunakan dictionary nested untuk representasi efisien dan akses cepat
- **DocumentLengthTable**: Kelas untuk menyimpan dan mengelola panjang dokumen
  - Menyimpan panjang setiap dokumen untuk normalisasi skor
  - Menghitung panjang rata-rata dokumen untuk perhitungan BM25
- **build_data_structures**: Fungsi koordinator yang membuat kedua struktur data dari korpus input

### 2. `parse.py` - Parser Data

File ini menangani pemrosesan file input dan preprocessing teks, yang mencakup pembacaan file, tokenisasi, dan pembersihan teks.

```python
# MODIFIKASI: Menambahkan fungsi untuk mendapatkan path absolut
def get_absolute_path(relative_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))  # src/
    parent_dir = os.path.dirname(current_dir)                # flask_app/ atau root direktori
    return os.path.join(parent_dir, relative_path)

class CorpusParser:

    def __init__(self, filename):
        # MODIFIKASI: Menambahkan dukungan untuk path absolut dan relatif
        self.filename = get_absolute_path(filename) if not os.path.isabs(filename) else filename
        self.corpus = dict()
        # MODIFIKASI: Menambahkan stopwords untuk preprocessing yang lebih baik
        self.stopwords = self.load_stopwords()

    # MODIFIKASI: Menambahkan fungsi preprocessing teks untuk meningkatkan kualitas pencarian
    def preprocess_text(self, text):
        # Case folding - mengubah teks menjadi lowercase
        text = text.lower()

        # Cleaning - menghapus tanda baca dan digit
        translator = str.maketrans('', '', string.punctuation + string.digits)
        text = text.translate(translator)

        # Tokenisasi - memecah teks menjadi token-token (kata-kata)
        tokens = text.split()

        # Filtering - menghapus stopwords
        tokens = [t for t in tokens if t not in self.stopwords]

        return tokens

    def parse(self):
        # MODIFIKASI: Mengubah parser untuk membaca file CSV yang lebih terstruktur
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                for i, row in enumerate(csv_reader):
                    docid = str(i)
                    title = row['Judul'] if 'Judul' in row else ''
                    content = row['Content'] if 'Content' in row else ''
                    link = row['Link'] if 'Link' in row else ''

                    # MODIFIKASI: Menyimpan metadata dokumen lengkap
                    self._full_corpus[docid] = {
                        'title': title,
                        'content': content,
                        'link': link
                    }

                    # MODIFIKASI: Menerapkan preprocessing ke judul dan konten
                    tokens = self.preprocess_text(title + ' ' + content)
                    self.corpus[docid] = tokens
```

**Komponen Utama:**

- **CorpusParser**: Kelas untuk memproses korpus dokumen
  - Membaca file CSV dengan metadata dokumen (judul, konten, URL)
  - Melakukan preprocessing teks (case folding, menghapus tanda baca, tokenisasi)
  - Menghilangkan stopwords yang tidak memiliki nilai semantik
- **QueryParser**: Kelas untuk memproses query pengguna
  - Menerima query dari CLI atau aplikasi web
  - Menerapkan preprocessing yang sama dengan korpus untuk konsistensi
- **Fungsi Utilitas Path**: Menangani path relatif dan absolut untuk konsistensi

### 3. `rank.py` - Algoritma BM25

File ini mengimplementasikan algoritma ranking BM25 untuk menghitung relevansi dokumen terhadap query pengguna.

```python
# MODIFIKASI: Parameter BM25 yang tetap sama dari versi original
k1 = 1.2
b = 0.75

# MODIFIKASI: Menambahkan fungsi untuk menghitung Term Frequency
def calculate_tf(raw_count, total_words):
    """
    Hitung Term Frequency sesuai rumus: TF(t,D) = Raw Count / Total Words in D

    Args:
        raw_count: Jumlah kemunculan term dalam dokumen
        total_words: Total kata dalam dokumen

    Returns:
        Term Frequency
    """
    return raw_count / total_words if total_words > 0 else 0


# MODIFIKASI: Menambahkan fungsi untuk menghitung Inverse Document Frequency
def calculate_idf(N, DF):
    """
    Hitung Inverse Document Frequency sesuai rumus:
    IDF = ln((N - DF + 0.5) / (DF + 0.5) + 1)

    Args:
        N: Jumlah total dokumen dalam corpus
        DF: Document frequency (jumlah dokumen yang mengandung term)

    Returns:
        Inverse Document Frequency
    """
    return log((N - DF + 0.5) / (DF + 0.5) + 1)


# MODIFIKASI: Merevisi fungsi score_BM25 untuk lebih jelas dan dengan parameter yang disederhanakan
def score_BM25(n, f, N, dl, avdl):
    """
    Hitung skor BM25 sesuai rumus:
    BM25(Q,D) = ∑ IDF(t) × (TF(t,D) × (k1 + 1)) / (TF(t,D) + k1 × (1 - b + b × |D|/avgD))

    Args:
        n: Document frequency (jumlah dokumen yang mengandung term)
        f: Raw frequency (jumlah kemunculan term dalam dokumen)
        N: Jumlah total dokumen
        dl: Document length (panjang dokumen)
        avdl: Average document length (rata-rata panjang dokumen)

    Returns:
        Skor BM25
    """
    # Hitung term frequency
    tf = calculate_tf(f, dl)

    # Hitung inverse document frequency
    idf = calculate_idf(N, n)

    # Hitung faktor normalisasi panjang dokumen
    K = compute_K(dl, avdl)

    # MODIFIKASI: Mengimplementasi rumus BM25 dengan lebih jelas
    tf_component = (tf * (k1 + 1)) / (tf + K)

    return idf * tf_component


def compute_K(dl, avdl):
    """
    Hitung faktor normalisasi panjang dokumen
    """
    return k1 * ((1-b) + b * (float(dl)/float(avdl)))
```

**Komponen Algoritma:**

- **Parameter Tuneable**: `k1` dan `b` yang mengontrol perilaku ranking
- **Fungsi Term Frequency**: Menghitung kepadatan term dalam dokumen
- **Fungsi Inverse Document Frequency**: Mengukur keunikan term dalam korpus
- **Fungsi Normalisasi Panjang**: Menyesuaikan skor berdasarkan panjang dokumen
- **Fungsi Skor Akhir**: Mengintegrasikan semua komponen untuk skor relevansi final

### 4. `query.py` - Pemrosesan Query

File ini menjalankan query terhadap indeks dan menghitung skor relevansi dokumen.

```python
class QueryProcessor:
    def __init__(self, queries, corpus):
        self.queries = queries
        self.index, self.dlt = build_data_structures(corpus)

    def run(self):
        results = []
        for query in self.queries:
            results.append(self.run_query(query))
        return results

    def run_query(self, query):
        query_result = dict()
        for term in query:
            if term in self.index:
                doc_dict = self.index[term] # retrieve index entry
                for docid, freq in doc_dict.items(): #for each document and its word frequency
                    # MODIFIKASI: Parameter skor BM25 disederhanakan, menghilangkan parameter tidak perlu
                    # - Parameter qf (query frequency) dan r (relevance feedback) dihapus
                    # - Menggunakan perhitungan BM25 yang lebih jelas
                    score = score_BM25(
                        n=len(doc_dict),
                        f=freq,
                        N=len(self.dlt),
                        dl=self.dlt.get_length(docid),
                        avdl=self.dlt.get_average_length()
                    )
                    if docid in query_result: #this document has already been scored once
                        query_result[docid] += score
                    else:
                        query_result[docid] = score
        return query_result
```

**Fitur Utama:**

- **Inisialisasi dengan Indeks**: Menggunakan struktur data yang telah dibangun sebelumnya
- **Pemrosesan Multi-Query**: Dapat memproses beberapa query sekaligus
- **Perhitungan Skor**: Menerapkan algoritma BM25 untuk setiap term dalam query
- **Akumulasi Skor**: Menjumlahkan kontribusi setiap term query ke skor dokumen final

### 5. `main.py` - Program Utama

File ini mengintegrasikan semua komponen dan menangani alur program dari input hingga output.

```python
def main():
    # MODIFIKASI: Menambahkan dukungan untuk argumen command line
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your search query\"")
        sys.exit(1)

    query_text = sys.argv[1]  # MODIFIKASI: Mengambil query dari argumen command line

    # MODIFIKASI: Menggunakan QueryParser dengan query langsung (bukan dari file)
    # Ini memungkinkan pencarian interaktif langsung dari command line
    qp = QueryParser(query=query_text)

    # MODIFIKASI: Mengubah path file corpus menjadi file CSV
    # File CSV menyimpan metadata dokumen yang lebih kaya (judul, konten, link)
    cp = CorpusParser(filename='text/data.csv')

    qp.parse()
    queries = qp.get_queries()

    cp.parse()

    corpus = cp.get_corpus()
    # MODIFIKASI: Mengambil korpus lengkap dengan metadata untuk hasil pencarian
    # Metadata (judul, konten, link) akan ditampilkan dalam hasil
    full_corpus = cp.get_full_corpus()

    proc = QueryProcessor(queries, corpus)
    results = proc.run()

    # MODIFIKASI: Mengubah format output untuk menampilkan hasil yang lebih informatif
    for result in results:
        sorted_x = sorted(result.items(), key=operator.itemgetter(1))
        sorted_x.reverse()

        # MODIFIKASI: Format output yang lebih mudah dibaca oleh pengguna
        print(f"\nSearch results for: '{query_text}'")
        print("-" * 80)

        # MODIFIKASI: Membatasi hasil ke 20 teratas untuk keterbacaan
        for i, (doc_id, score) in enumerate(sorted_x[:20]):
            # MODIFIKASI: Mengambil metadata dokumen dari full_corpus
            doc_data = full_corpus[doc_id]
            title = doc_data['title']
            link = doc_data['link']
            content = doc_data['content']

            # MODIFIKASI: Memotong konten yang terlalu panjang untuk keterbacaan
            if len(content) > 200:
                content = content[:200] + "..."

            # MODIFIKASI: Menampilkan hasil dalam format yang mudah dibaca dengan metadata lengkap
            print(f"{i+1}. {title}")
            print(f"   Link: {link}")
            print(f"   Score: {score:.6f}")
            print(f"   Content: {content}")
            print("-" * 80)
```

**Alur Program:**

- **Parsing Argumen**: Mengambil query dari command line arguments
- **Preprocessing Data**: Mempersiapkan korpus dan query untuk pencarian
- **Eksekusi Query**: Menjalankan proses pencarian menggunakan QueryProcessor
- **Pengurutan & Presentasi**: Mengurutkan hasil berdasarkan skor dan menampilkannya dengan format yang informatif
- **Metadata Kaya**: Menampilkan judul, URL, dan cuplikan konten untuk setiap hasil

Struktur kode ini menerapkan prinsip modularitas yang baik, dengan pemisahan yang jelas antara indeks, parsing, ranking, dan pemrosesan query. Pendekatan ini memudahkan pemeliharaan, pengujian, dan pengembangan lebih lanjut di masa depan.

## Alur Proses Pencarian

Berikut adalah alur lengkap proses pencarian dari input hingga output:

### 1. Input Query dari Pengguna

```bash
python src/main.py "contoh query pencarian"
```

Query dari command line diteruskan ke sistem.

### 2. Preprocessing Query

`QueryParser` memproses query melalui tahapan:

- **Case folding**: Mengubah semua huruf menjadi lowercase
- **Cleaning**: Menghapus tanda baca dan angka
- **Tokenisasi**: Memecah query menjadi kata-kata
- **Filtering**: Menghapus stopwords

Contoh:

```
Input: "Machine Learning Algorithm 2023!"
Setelah preprocessing: ["machine", "learning", "algorithm"]
```

### 3. Pembacaan dan Preprocessing Korpus

`CorpusParser` membaca file CSV dan memproses setiap dokumen:

- Membaca metadata (judul, konten, link)
- Melakukan preprocessing teks (sama seperti query)
- Menyimpan dokumen asli dan token hasil preprocessing

```python
self.corpus[docid] = {
    'title': title,
    'content': content,
    'link': link,
    'tokens': self.preprocess_text(title + ' ' + content)
}
```

### 4. Pembangunan Inverted Index

Dari token-token dokumen, sistem membangun:

- **Inverted index**: Memetakan term ke dokumen dan frekuensi
- **Document length table**: Menyimpan jumlah token di setiap dokumen

Contoh indeks:

```
{
    "machine": {"0": 3, "4": 1, "7": 2},  # Term "machine" muncul 3x di dok.0, 1x di dok.4, dsb
    "learning": {"0": 2, "2": 1, "4": 2},
    "algorithm": {"0": 1, "3": 4, "7": 2}
}
```

### 5. Pemrosesan Query dan Perhitungan BM25

Untuk setiap term dalam query, sistem:

1. Mencari dokumen yang mengandung term
2. Untuk tiap dokumen, menghitung skor BM25:
   - Menghitung TF (Term Frequency)
   - Menghitung IDF (Inverse Document Frequency)
   - Menghitung faktor normalisasi panjang K
   - Menghitung komponen TF dengan saturasi
   - Mengalikan IDF dengan komponen TF
3. Mengakumulasikan skor dari semua term query

### 6. Pengurutan dan Penampilan Hasil

Hasil akhir:

1. Dokumen-dokumen diurutkan berdasarkan total skor (tertinggi ke terendah)
2. 20 dokumen teratas ditampilkan dengan metadata:
   - Judul dokumen
   - URL/link dokumen
   - Skor BM25
   - Cuplikan konten

## Cara Menjalankan Kode

### Persiapan

1. Pastikan file CSV dengan data dokumen tersedia di direktori `text/data.csv`.
2. File CSV harus memiliki struktur:

```csv
Judul,Content,Link
"Dokumen 1","Isi konten dokumen pertama...","https://example.com/doc1"
"Dokumen 2","Isi konten dokumen kedua...","https://example.com/doc2"
...
```

3. Pastikan file stopwords tersedia di direktori `text/stopword.txt`. Formatnya:

```
kata1
kata2
// komentar tidak diproses
kata3
...
```

### Menjalankan Pencarian

Gunakan perintah:

```bash
python src/main.py "query pencarian anda"
```

Contoh:

```bash
python src/main.py "machine learning algorithm"
```

### Demo Langkah demi Langkah

#### 1. Input Query

```bash
python src/main.py "artificial intelligence deep learning"
```

#### 2. Preprocessing Query

```python
# Query setelah preprocessing:
["artificial", "intelligence", "deep", "learning"]
```

#### 3. Pembacaan Korpus dan Pembangunan Indeks

```python
# Di file main.py
cp = CorpusParser(filename='text/data.csv')
cp.parse()
corpus = cp.get_corpus()
full_corpus = cp.get_full_corpus()
```

#### 4. Perhitungan BM25 dan Perankingan

```python
proc = QueryProcessor(queries, corpus)
results = proc.run()
# Pengurutan hasil
sorted_x = sorted(result.items(), key=operator.itemgetter(1))
sorted_x.reverse()
```

#### 5. Menampilkan Hasil

```python
for i, (doc_id, score) in enumerate(sorted_x[:20]):
    doc_data = full_corpus[doc_id]
    title = doc_data['title']
    link = doc_data['link']
    content = doc_data['content']
    # Tampilkan hasil dengan format yang rapi
    print(f"{i+1}. {title}")
    print(f"   Link: {link}")
    print(f"   Score: {score:.6f}")
    print(f"   Content: {content[:200]}...")
```

## Contoh Output

Berikut adalah contoh output dari program:

```
Search results for: 'artificial intelligence deep learning'
--------------------------------------------------------------------------------
1. Introduction to Artificial Intelligence
   Link: https://example.com/intro-ai
   Score: 1.842567
   Content: Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals and humans...
--------------------------------------------------------------------------------
2. Deep Learning: A Comprehensive Guide
   Link: https://example.com/deep-learning
   Score: 1.654321
   Content: Deep learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning...
--------------------------------------------------------------------------------
3. AI and Deep Learning Applications
   Link: https://example.com/ai-apps
   Score: 1.234567
   Content: The applications of artificial intelligence and deep learning are revolutionizing industries from healthcare to finance...
--------------------------------------------------------------------------------
```

## Perbandingan dengan Kode Awal

### 1. Format Input Data

**Kode Original**:

- File teks dengan format: `#1 ini adalah dokumen satu #2 ini dokumen dua...`
- Tidak ada struktur metadata
- Parser yang kaku dengan regex

**Kode Modifikasi**:

- File CSV dengan header dan kolom terstruktur (Judul, Content, Link)
- Menyimpan metadata yang dapat ditampilkan dalam hasil
- Parser yang fleksibel menggunakan modul CSV

### 2. Preprocessing Teks

**Kode Original**:

- Tidak ada preprocessing khusus
- Tidak ada penanganan kasus huruf
- Tidak menghapus tanda baca atau stopwords

**Kode Modifikasi**:

- Case folding untuk konsistensi pencarian
- Menghapus tanda baca dan angka
- Tokenisasi yang lebih baik
- Menghapus stopwords untuk meningkatkan relevansi

### 3. Implementasi BM25

**Kode Original**:

```python
def score_BM25(n, f, qf, r, N, dl, avdl):
    K = compute_K(dl, avdl)
    first = log( ( (r + 0.5) / (R - r + 0.5) ) / ( (n - r + 0.5) / (N - n - R + r + 0.5)) )
    second = ((k1 + 1) * f) / (K + f)
    third = ((k2+1) * qf) / (k2 + qf)
    return first * second * third
```

**Kode Modifikasi**:

```python
def score_BM25(n, f, N, dl, avdl):
    tf = calculate_tf(f, dl)
    idf = calculate_idf(N, n)
    K = compute_K(dl, avdl)
    tf_component = (tf * (k1 + 1)) / (tf + K)
    return idf * tf_component
```

Perubahan:

- Pemisahan logika ke fungsi-fungsi terpisah untuk TF dan IDF
- Penghapusan parameter yang tidak perlu (qf, r, R)
- Dokumentasi yang lebih jelas

### 4. Interface Pengguna

**Kode Original**:

- Input queries dari file
- Format output tabular yang sulit dibaca

```
0	Q0	   1	 0	   0.756423	NH-BM25
0	Q0	   4	 1	   0.634982	NH-BM25
```

**Kode Modifikasi**:

- Input query dari command line
- Format output yang lebih informatif dan mudah dibaca

```
Search results for: 'machine learning'
--------------------------------------------------------------------------------
1. Introduction to Machine Learning
   Link: https://example.com/intro-ml
   Score: 0.756423
   Content: Machine learning is a branch of artificial intelligence...
--------------------------------------------------------------------------------
```

### 5. Penanganan File dan Path

**Kode Original**:

- Path hardcoded
- Tidak ada penanganan error

**Kode Modifikasi**:

- Mendukung path relatif dan absolut
- Penanganan error yang lebih baik
- Dukungan encoding UTF-8 untuk file

## Implementasi Web dengan Flask

Selain implementasi command line, algoritma BM25 juga diimplementasikan dalam bentuk aplikasi web menggunakan framework Flask. Aplikasi web ini menyediakan antarmuka pengguna yang lebih interaktif dan visual, memudahkan pengguna untuk melakukan pencarian tanpa perlu berinteraksi dengan command line.

### Struktur Aplikasi Flask

Aplikasi web BM25 memiliki struktur folder yang terorganisir sebagai berikut:

```
flask_app/
├── app.py                  # File utama aplikasi Flask
├── requirements.txt        # Dependensi untuk aplikasi Flask
├── README.md              # Dokumentasi aplikasi Flask
├── static/
│   └── style.css          # CSS untuk styling aplikasi web
├── templates/
│   ├── index.html         # Template halaman utama dengan form pencarian
│   └── search.html        # Template halaman hasil pencarian
└── text/
    ├── data.csv           # Dataset dokumen dalam format CSV
    └── stopword.txt       # Daftar stopwords untuk preprocessing
```

Struktur ini mengikuti konvensi Flask dengan pemisahan yang jelas antara:

- Kode aplikasi utama (`app.py`)
- Template HTML (`templates/`)
- File statis seperti CSS (`static/`)
- Data yang diperlukan aplikasi (`text/`)

Pendekatan ini memudahkan pengembangan dan pemeliharaan aplikasi web secara terpisah dari implementasi algoritma utama.

### Penjelasan Detail Kode Flask

#### 1. Kode `app.py` - Aplikasi Utama Flask

File `app.py` adalah inti dari aplikasi web yang menangani permintaan HTTP, memproses pencarian, dan merender hasil. Berikut penjelasan detail komponen-komponennya:

```python
import os
import sys

from flask import Flask, request, render_template
from src.parse import CorpusParser, QueryParser
from src.query import QueryProcessor

app = Flask(__name__)

data_path = os.path.join(os.path.dirname(__file__), 'text', 'data.csv')

# MODIFIKASI: Inisialisasi corpus di awal aplikasi untuk performa yang lebih baik
cp = CorpusParser(filename=data_path)
cp.parse()
corpus = cp.get_corpus()
full_corpus = cp.get_full_corpus()

@app.route('/', methods=['GET'])
def home():
    """Halaman utama dengan form pencarian"""
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    """Halaman hasil pencarian"""
    query_text = request.args.get('q', '')

    if not query_text:
        return render_template('index.html')

    # MODIFIKASI: Proses query menggunakan algoritma BM25
    qp = QueryParser(query=query_text)
    qp.parse()
    queries = qp.get_queries()
    proc = QueryProcessor(queries, corpus)
    results = proc.run()

    search_results = []
    if results:
        for result in results:
            # MODIFIKASI: Pengurutan hasil berdasarkan skor BM25
            sorted_results = sorted(result.items(), key=lambda x: x[1], reverse=True)
            for doc_id, score in sorted_results[:20]:
                # MODIFIKASI: Mengambil metadata dokumen dari corpus lengkap
                doc_data = full_corpus[doc_id]
                title = doc_data['title']
                link = doc_data['link']
                content = doc_data['content']
                snippet = content[:200] + "..." if len(content) > 200 else content
                search_results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'score': score
                })

    return render_template('search.html', query=query_text, results=search_results)

if __name__ == '__main__':
    app.run(debug=True)
```

#### 2. Template HTML - Antarmuka Pengguna

Template HTML digunakan untuk merender antarmuka pengguna aplikasi web. Flask menggunakan engine template Jinja2 yang memungkinkan pemisahan logika aplikasi dari tampilan.

##### `index.html` - Halaman Utama Pencarian

```html
<!DOCTYPE html>
<html lang="id">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>BM25 Search Engine</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='style.css') }}"
    />
  </head>
  <body>
    <div class="container search-container">
      <div class="search-header">
        <div class="logo">
          <span>S</span><span>e</span><span>a</span><span>r</span><span>c</span
          ><span>h</span>
        </div>
        <div class="search-box">
          <form action="/search" method="GET" class="search-form">
            <input
              type="text"
              name="q"
              class="search-input"
              placeholder="Masukkan kata kunci pencarian..."
              autofocus
              required
            />
            <button type="submit" class="search-button">Cari</button>
          </form>
        </div>
      </div>
    </div>
  </body>
</html>
```

##### `search.html` - Halaman Hasil Pencarian

```html
<!DOCTYPE html>
<html lang="id">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{ query }} - Hasil Pencarian</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='style.css') }}"
    />
  </head>
  <body>
    <div class="container">
      <div class="search-results-header">
        <div class="logo">
          <span>S</span><span>e</span><span>a</span><span>r</span><span>c</span
          ><span>h</span>
        </div>
        <div class="search-box">
          <form action="/search" method="GET" class="search-form">
            <input
              type="text"
              name="q"
              class="search-input"
              value="{{ query }}"
              required
            />
            <button type="submit" class="search-button">Cari</button>
          </form>
        </div>
      </div>

      <div class="search-results">
        <div class="search-stats">
          Sekitar {{ results|length }} hasil untuk
          <strong>"{{ query }}"</strong>
        </div>

        {% if results %} {% for result in results %}
        <div class="result">
          <div class="result-title">
            <a href="{{ result.link }}" target="_blank">{{ result.title }}</a>
          </div>
          <div class="result-url">{{ result.link }}</div>
          <div class="result-snippet">{{ result.snippet }}</div>
          <div class="result-score">Score: {{ result.score|round(6) }}</div>
        </div>
        {% endfor %} {% else %}
        <div class="no-results">
          <p>Tidak ditemukan hasil untuk pencarian Anda.</p>
          <p>Saran:</p>
          <ul>
            <li>Periksa ejaan kata kunci pencarian Anda</li>
            <li>Coba kata kunci yang berbeda</li>
            <li>Coba kata kunci yang lebih umum</li>
          </ul>
        </div>
        {% endif %}
      </div>
    </div>
  </body>
</html>
```

### Cara Menjalankan Aplikasi Flask

Untuk menjalankan aplikasi web BM25, ikuti langkah-langkah berikut:

#### 1. **Instalasi Dependensi**

Aplikasi web Flask membutuhkan beberapa dependensi yang perlu diinstal terlebih dahulu:

```bash
pip install -r flask_app/requirements.txt
```

Dependensi yang digunakan pada aplikasi web meliputi:

```
flask==2.2.3         # Framework web Python yang ringan dan fleksibel
Werkzeug==2.2.3      # Library WSGI yang digunakan Flask untuk menangani request
Jinja2==3.1.2        # Engine template untuk merender HTML
MarkupSafe==2.1.2    # Library untuk menangani string dengan aman di template
itsdangerous==2.1.2  # Library untuk penandatanganan data dengan aman
click==8.1.3         # Library untuk membuat aplikasi command-line
```

#### 2. **Menjalankan Aplikasi Web**

Setelah semua dependensi terinstal, jalankan aplikasi dengan perintah berikut:

```bash
cd flask_app
python app.py
```

Server development Flask akan berjalan dan aplikasi akan tersedia di `localhost` port 5000.

#### 3. **Mengakses Aplikasi**

Setelah aplikasi berjalan, buka browser web dan navigasikan ke:

```
http://127.0.0.1:5000/
```

Halaman pencarian utama akan tampil dan Anda dapat langsung mulai mencari dengan memasukkan kata kunci pada form yang tersedia.

#### 4. **Melakukan Pencarian**

- Masukkan kata kunci atau frasa pada kotak pencarian
- Tekan tombol "Cari" atau tekan Enter
- Hasil pencarian yang relevan akan ditampilkan, diurutkan berdasarkan skor relevansi BM25

### Tampilan Aplikasi Web

#### Halaman Utama (Search Form)

![Halaman Utama BM25 Search](https://i.imgur.com/fKGTIyV.png)

#### Halaman Hasil Pencarian

![Halaman Hasil Pencarian BM25](https://i.imgur.com/yIfL9p5.png)
