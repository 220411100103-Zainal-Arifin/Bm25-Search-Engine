__author__ = 'Nick Hirakawa'

import re
import csv
import string
import os

# Get absolute paths relatif terhadap flask_app
def get_absolute_path(relative_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))  # src/
    parent_dir = os.path.dirname(current_dir)                # flask_app/
    return os.path.join(parent_dir, relative_path)

class CorpusParser:

	def __init__(self, filename):
		self.filename = get_absolute_path(filename) if not os.path.isabs(filename) else filename
		self.corpus = dict()
		self.stopwords = self.load_stopwords()
		
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
	
	def preprocess_text(self, text):
		# Case folding
		text = text.lower()
		
		# Cleaning - remove punctuation and digits
		translator = str.maketrans('', '', string.punctuation + string.digits)
		text = text.translate(translator)
		
		# Tokenize
		tokens = text.split()
		
		# Remove stopwords
		tokens = [t for t in tokens if t not in self.stopwords]
		
		return tokens

	def parse(self):
		try:
			with open(self.filename, 'r', encoding='utf-8') as f:
				csv_reader = csv.DictReader(f)
				for i, row in enumerate(csv_reader):
					docid = str(i)
					title = row['Judul'] if 'Judul' in row else ''
					content = row['Content'] if 'Content' in row else ''
					link = row['Link'] if 'Link' in row else ''
					
					# Store original data for display in results
					self.corpus[docid] = {
						'title': title,
						'content': content,
						'link': link,
						'tokens': self.preprocess_text(title + ' ' + content)
					}
		except Exception as e:
			print(f"Error parsing corpus from {self.filename}: {e}")
			raise

	def get_corpus(self):
		corpus_for_indexing = {}
		for docid, doc_data in self.corpus.items():
			corpus_for_indexing[docid] = doc_data['tokens']
		return corpus_for_indexing
		
	def get_full_corpus(self):
		return self.corpus


class QueryParser:

	def __init__(self, query=None, filename=None):
		self.filename = get_absolute_path(filename) if filename and not os.path.isabs(filename) else filename
		self.query = query
		self.queries = []
		self.stopwords = self.load_stopwords()
	
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
	
	def preprocess_text(self, text):
		# Case folding
		text = text.lower()
		
		# Cleaning - remove punctuation and digits
		translator = str.maketrans('', '', string.punctuation + string.digits)
		text = text.translate(translator)
		
		# Tokenize
		tokens = text.split()
		
		# Remove stopwords
		tokens = [t for t in tokens if t not in self.stopwords]
		
		return tokens

	def parse(self):
		if self.query:
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
	qp = QueryParser(filename='text/queries.txt')
	qp.parse()
	print(qp.get_queries())
