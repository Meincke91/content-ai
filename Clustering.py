import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.cluster import AffinityPropagation
from sklearn import preprocessing
import pandas as pd
import matplotlib.pyplot as plt
import pickle

#df = getdata
class Clustering():

	def train_affinity_propogation_model(self, X, savePickle = True):
		clf = AffinityPropagation(preference=-50).fit(X)
		cluster_centers_indices = clf.cluster_centers_indices_

		if savePickle:
			with open('affinity_propagation.pickle','wb') as f:
				pickle.dump(clf, f)

		return clf

	def load_affinity_propogation_model_pickle(self):
		pickle_in = open('affinity_propagation.pickle', 'rb')
		clf = pickle.load(pickle_in)

		return clf

	def train_mean_shift_model(self, X, savePickle = True):
		X = preprocessing.scale(X)

		bandwidth = estimate_bandwidth(X, quantile=0.1, n_samples=500)

		clf = MeanShift(bandwidth=bandwidth, bin_seeding=True)
		clf.fit(X)
		if savePickle:
			with open('meanshift.pickle','wb') as f:
				pickle.dump(clf, f)

		return clf

	def load_mean_shift_model_pickle(self):
		pickle_in = open('meanshift.pickle', 'rb')
		clf = pickle.load(pickle_in)

		return clf