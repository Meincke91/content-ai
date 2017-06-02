from mysqldb import Mysqldb
from config import *
from nltk.corpus import stopwords

class PrepareData():
	"""docstring for ClassName"""
	def __init__(self, db):
		self.db = db
	
	def NLTKremoveStopWords(self, words):
		stop_words = set(stopwords.words('english'))

		outputWords = []

		for word in words:
			if not word in stop_words:
				outputWords.append(word)
		print(outputWords)

	def NLTKremoveStopWordsFromDict(self, inputWords):
		stop_words = set(stopwords.words('english'))

		outputWords = {}

		for word, value in inputWords.items():
			if not word in stop_words:
				outputWords[word] = value
		return outputWords


	def removeStopWordsFromDict(self, inputWords):
		stop_words = self.db.selectWordsInRange(0,10)

		outputWords = {}
		for word, value in inputWords.items():
			if not word in stop_words:
				outputWords[word] = value

		return outputWords

	def remove 

if __name__ == '__main__':
	prepareData = PrepareData()
	prepareData.removeStopWords(["one"])