from mysqldb import Mysqldb
from config import *
import numpy as np
import operator
from math import log2
from prepareData import PrepareData

class WordClustering():
	def __init__(self, db):
		self.db = db
		self.prepareData = PrepareData(db)

	def collectWords(self):
		words = self.db.selectWordsInRange(30,  60)
		print(words[:100])

	def findLinksFromKeywords(self, keywords):
		wordIds = []

		for keyword in keywords:
			wordIds.append(self.db.selectWord(keyword))

		articleIds = self.db.selectArticleFromWords(wordIds)
		collectiveWords = {}

		for articleId in articleIds:
			words = self.db.selectWordsFromArticle(articleId)

			for word, count in words.items():
				
				if not word in collectiveWords:
					collectiveWords[word] = count
				else:
					collectiveWords[word] = collectiveWords[word] + count

		topicWords = self.prepareData.NLTKremoveStopWordsFromDict(collectiveWords)
		sorted_x = sorted(topicWords.items(), key=operator.itemgetter(1))

		for x in sorted_x[int(len(sorted_x)*0.95):]:
			print("%s, %s" % (self.db.selectWordFromId(x[0]), x[1]))
		
	def calculateTDIDF(self, keyword, article):
		wordId = self.db.selectWord(keyword)
		
		articleIds = self.db.selectArticleFromWords([wordId])
		N = self.db.selectArticleSize()

		IDF = log2(N/len(articleIds))

		article = articleIds[0]

		words = self.db.selectWordsFromArticle(article)
		baseWordCount = words[wordId]

		words = self.prepareData.NLTKremoveStopWordsFromDict(words)

		# even if stopword calculate the TD.IDF
		if not wordId in words or words[wordId] is None:
			words[wordId] = baseWordCount

		sorted_x = sorted(words.items(), key=operator.itemgetter(1))
		TF = baseWordCount / sorted_x[len(sorted_x)-1][1]
		TFIDF = TF * IDF
		return TFIDF



if __name__ == '__main__':
	with Mysqldb(**mysqlconfig) as db:
		wordClustering = WordClustering(db)
		print(wordClustering.calculateTDIDF("leukemia",0))
		print(wordClustering.calculateTDIDF("medical",0))
		#wordClustering.findLinksFromKeywords(['leukemia'])