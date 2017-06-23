from PrepareData import PrepareData
from collections import Counter
from Mysqldb import Mysqldb

import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle
from datetime import datetime, timedelta

from config import *
from medicalTerms import *

class Plots():
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

	def plotScatter(self, dict=None, array=None):
		x = []
		y = []

		if not dict is None:
			for key, value in dict.items():
				x.append(key)
				y.append(value)
		else:
			count = 0
			for value in array:
				x.append(count)
				y.append(value)
				count = count + 1


		# red dashes, blue squares and green triangles
		plt.plot(x, y, 'ro')
		plt.ylabel('Average TF.IDF')
		plt.xlabel('Resources ordered by time')
		plt.show()

	def plotMeanShiftClusters(self, clf, X):
		plt.figure(1)
		plt.clf()

		cluster_centers = clf.cluster_centers_

		labels = clf.labels_
		labels_unique = np.unique(labels)
		n_clusters_ = len(labels_unique)

		colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
		for k, col in zip(range(n_clusters_), colors):
		    my_members = labels == k
		    cluster_center = cluster_centers[k]
		    plt.plot(X[0], X[1], col + '.')
		    plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
		             markeredgecolor='k', markersize=14)
		plt.title('Estimated number of clusters: %d' % n_clusters_)
		plt.show()

	def tweetWordHistrogram(self, hoursDelta, baseLineTimeDelta):
		d = datetime.now() - timedelta(hours=hoursDelta)
		texts=self.db.selectTweetText(d.strftime("%Y-%m-%d %H:%M:%S"))

		baseLineD = datetime.now() - timedelta(hours=baseLineTimeDelta)
		baseLineTexts=self.db.selectTweetText(baseLineD.strftime("%Y-%m-%d %H:%M:%S"))

		finalWords = []
		for text in texts:
			words = text.split(' ')
			words = self.prepareData.NLTKremoveStopWords(words)
			for word in words:
				if word in medicalTerms:
					finalWords.append(word)

		finalBaseWords = []
		for text in baseLineTexts:
			baseLineWords = text.split(' ')
			baseLineWords = self.prepareData.NLTKremoveStopWords(baseLineWords)
			for baseWord in baseLineWords:
				if baseWord in finalWords:
					finalBaseWords.append(baseWord)

		counts = Counter(finalWords)
		avgDict = {}
		for key, value in Counter(finalBaseWords).items():
			print("%s avg: %s, current: %s" % (key, value/len(baseLineTexts), counts[key]/len(texts)))
			avgDict[key] = (counts[key]/len(texts))/(value/len(baseLineTexts))
		
		
		#print(counts['cancer'])
		labels, values = zip(*avgDict.items())

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
