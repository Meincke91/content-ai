import numpy as np
import matplotlib.pyplot as plt
from mysqldb import Mysqldb
from config import *
from datetime import datetime, timedelta
from prepareData import PrepareData
from medicalTerms import *
from collections import Counter



class PlotData():
	"""docstring for ClassName"""
	def __init__(self, db):
		self.db = db
		self.prepareData = PrepareData(db)
		
	def plotExample(self):
		# evenly sampled time at 200ms intervals

		tfidf0 = []
		lix0 = []
		tfidf1 = []
		lix1 = []

		dictionary = self.db.selectArticlTfidfAndLix(limit=10000)
		for key, value in dictionary.items():
			if value[2] == 1:
				tfidf1.append(value[0])
				lix1.append(value[1])
			else:
				tfidf0.append(value[0])
				lix0.append(value[1])

		# red dashes, blue squares and green triangles
		plt.plot(tfidf1, lix1, 'ro', tfidf0, lix0, 'bo', )
		plt.show()

	def tweetWordHistrogram(self, hoursDelta, baseLineTimeDelta):
		d = datetime.now() - timedelta(hours=hoursDelta)
		texts=self.db.selectTweetText(d.strftime("%Y-%m-%d %H:%M:%S"))
		finalWords = []
		for text in texts:
			words = text.split(' ')
			words = self.prepareData.NLTKremoveStopWords(words)
			for word in words:
				if word in medicalTerms:
					finalWords.append(word)

		counts = Counter(finalWords)

		labels, values = zip(*counts.items())

		# sort your values in descending order
		indSort = np.argsort(values)[::-1]

		# rearrange your data
		labels = np.array(labels)[indSort]
		values = np.array(values)[indSort]

		indexes = np.arange(len(labels))

		bar_width = 0.35

		plt.bar(indexes, values)

		# add labels
		plt.xticks(indexes + bar_width, labels)
		plt.show()
		#print(wordHist)


if __name__ == '__main__':
	with Mysqldb(**mysqlconfig) as db:
		plotData = PlotData(db)
		plotData.tweetWordHistrogram(24, 2400)
