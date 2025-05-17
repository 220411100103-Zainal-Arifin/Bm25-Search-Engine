__author__ = 'Nick Hirakawa'


from math import log

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