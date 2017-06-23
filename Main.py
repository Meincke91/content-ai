from Mysqldb import Mysqldb
from Webscraper import WebScraper
from NeuralNetwork import NeuralNetwork
from PrepareData import PrepareData
from RandomForest import RandomForest
from Clustering import Clustering
from Plots import Plots
from Webcrawl import WebCrawler

import pickle
import operator
import numpy as np

from config import *
from medicalTerms import *

class Main():
	def __init__(self, db):
		self.db = db
		self.prepareData = PrepareData(db)
		self.clustering = Clustering()
		self.plots = Plots(db)
		self.webCrawler = WebCrawler(db)

	def calculateAffinityPropagation(self):
		X = self.prepareData.getTrainingData()
		clf = self.clustering.train_affinity_propogation_model(X)
		return clf

	def loadAffinityPropagation(self):
		clf = self.clustering.load_affinity_propogation_model_pickle()
		return clf

	def calculateMeanShift(self):
		X = self.prepareData.getTrainingData()
		clf = self.clustering.train_mean_shift_model(X)
		return clf

	def loadMeanShift(self):
		clf = self.clustering.load_mean_shift_model_pickle()
		return clf

	def plotMeanShift(self, clf):
		X = self.prepareData.getTrainingData()
		self.plots.plotMeanShiftClusters(clf, X)

	def calculateTFIDF(self, keyword):
		tfidfs = self.prepareData.calculateTFIDFs(keyword)
		sorted_tfidfs = sorted(tfidfs.items(), key=operator.itemgetter(1))
		print(sorted_tfidfs)

	def plotTimeTFIDF(self, keywords, loadPickle=True):
		

		if loadPickle:
			pickle_in = open('allTfidf.pickle', 'rb')
			tfidfs = pickle.load(pickle_in)
		else:
			tfidfs = self.prepareData.calculateAllTFIDFs(keywords)
			with open('allTfidf.pickle','wb') as f:
				pickle.dump(tfidfs, f)
		dict2 = {}
		count = 0
		for key, value in tfidfs.items():
			if count > 16100:
				dict2[key] = value
			count = count + 1
		self.plots.plotScatter(array=self.prepareData.groupDictValues(dict2, 3000))
		self.plots.plotScatter(dict=dict2)

	def startCrawl(self, keywords):
		self.webCrawler.tfidfSpider(keywords)


if __name__ == '__main__':
	with Mysqldb(**mysqlconfig) as db:
		mainProgram = Main(db)
		#mainProgram.plotTimeTFIDF(["fibrosis"], loadPickle=True)
		mainProgram.startCrawl(medicalTerms)
		"""clf = mainProgram.loadAffinityPropagation()
		for cluster_id in np.unique(clf.labels_):
			#exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
			#cluster = np.unique(words[np.nonzero(affprop.labels_==cluster_id)])
			#cluster_str = ", ".join(cluster)
			#print(" - *%s:* %s" % (exemplar, cluster_str))
			print()
			print(cluster_id)
			print(np.nonzero(clf.labels_==cluster_id))"""
		#mainProgram.plotMeanShift(clf)

		
		