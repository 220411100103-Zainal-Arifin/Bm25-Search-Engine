__author__ = 'Nick Hirakawa'

import re
import csv  # MODIFIKASI: Menambahkan modul csv untuk membaca file CSV dengan format terstruktur
import string  # MODIFIKASI: Menambahkan modul string untuk operasi string (seperti menghapus tanda baca)
import os  # MODIFIKASI: Menambahkan modul os untuk operasi path file

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
        
    # MODIFIKASI: Menambahkan fungsi untuk memuat stopwords dari file
    def load_stopwords(self):
        stopwords = set()
        try:
            stopwords_path = get_absolute_path('text/stopword.txt')
            with open(stopwords_path, 'r') as f:
                for line in f:
                    word = line.strip()
                    if word and not word.startswith('//'):
                        stopwords.add(word.lower())
        except Exception as e:
            print(f"Warning: Could not load stopwords: {e}")
        return stopwords
    
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
                    
                    # MODIFIKASI: Menyimpan data asli dan token hasil preprocessing
                    self.corpus[docid] = {
                        'title': title,
                        'content': content,
                        'link': link,
                        'tokens': self.preprocess_text(title + ' ' + content)
                    }
        except Exception as e:
            print(f"Error parsing corpus from {self.filename}: {e}")
            raise

    # MODIFIKASI: Mengubah get_corpus() untuk mereturn hanya token yang sudah diproses
    def get_corpus(self):
        corpus_for_indexing = {}
        for docid, doc_data in self.corpus.items():
            corpus_for_indexing[docid] = doc_data['tokens']
        return corpus_for_indexing
        
    # MODIFIKASI: Menambahkan fungsi untuk mendapatkan korpus lengkap termasuk metadata
    def get_full_corpus(self):
        return self.corpus


class QueryParser:

    def __init__(self, query=None, filename=None):
        # MODIFIKASI: Menambahkan dukungan untuk query langsung dan file
        self.filename = get_absolute_path(filename) if filename and not os.path.isabs(filename) else filename
        self.query = query
        self.queries = []
        # MODIFIKASI: Menambahkan stopwords untuk konsistensi preprocessing dengan korpus
        self.stopwords = self.load_stopwords()
    
    # MODIFIKASI: Menambahkan fungsi untuk memuat stopwords
    def load_stopwords(self):
        stopwords = set()
        try:
            stopwords_path = get_absolute_path('text/stopword.txt')
            with open(stopwords_path, 'r') as f:
                for line in f:
                    word = line.strip()
                    if word and not word.startswith('//'):
                        stopwords.add(word.lower())
        except Exception as e:
            print(f"Warning: Could not load stopwords: {e}")
        return stopwords

    # MODIFIKASI: Menambahkan fungsi preprocessing teks yang sama dengan CorpusParser
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

    # MODIFIKASI: Mengubah parse() untuk mendukung query langsung
    def parse(self):
        if self.query:
            # Jika ada query langsung, preprocess dan simpan
            self.queries = [self.preprocess_text(self.query)]
        elif self.filename:
            try:
                with open(self.filename) as f:
                    lines = ''.join(f.readlines())
                self.queries = [self.preprocess_text(x.rstrip()) for x in lines.split('\n') if x.strip()]
            except Exception as e:
                print(f"Error parsing queries from {self.filename}: {e}")
                raise

    def get_queries(self):
        return self.queries


if __name__ == '__main__':
    # MODIFIKASI: Contoh penggunaan dengan filename
    qp = QueryParser(filename='text/queries.txt')
    qp.parse()
    print(qp.get_queries())
