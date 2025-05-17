__author__ = 'Nick Hirakawa'

from parse import *
from query import QueryProcessor
import operator
import sys  # MODIFIKASI: Menambahkan modul sys untuk mendukung argumen command line


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


if __name__ == '__main__':
    main()
