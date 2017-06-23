
from Mysqldb import Mysqldb
from PrepareData import PrepareData

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np
import pickle

from config import *

class RandomForest():
	"""docstring for ClassName"""
	def __init__(self, db):
		self.prepareData = PrepareData(db)
		

	def trainRandomForestClassifier(self, X, Y):
		clf = RandomForestClassifier(n_estimators=10, max_depth=2)
		print(X[0])
		clf = clf.fit(X, Y)

		with open('randomforest.pickle','wb') as f:
			pickle.dump(clf, f)

		return clf

	def testIris(self, X, Y):
		xdf = pd.DataFrame(X)
		ydf = pd.DataFrame(Y)
		#iris = load_iris()
		#df = pd.DataFrame(iris.data, columns=iris.feature_names)
		#df['is_train'] = np.random.uniform(0, 1, len(df)) <= .75
		#df['species'] = pd.Categorical(iris.target, iris.target_names)
		#train, test = df[df['is_train']==True], df[df['is_train']==False]
		
		#features = df.columns[:4]
		clf = RandomForestClassifier(n_jobs=2)
		#y, _ = pd.factorize(train['species'])
		clf.fit(xdf, ydf)
		print(clf)
		#print("iris: %s" % (y))
		#print("x: %s" % (ydf))
		#print(train[features])

	def prepareDataForForrest(self):
		documents, classes, words = self.prepareData.getTrainingDocuments(self.prepareData.getRealData())
		X, Y = self.prepareData.training_set(documents, classes, words)
		print("len x: %s,  len y: %s " % (len(X), len(Y)))
		per = 90
		perIndex = int(len(X)*(80/100))

		X_train = np.array(X[:perIndex])
		X_test = np.array(X[perIndex:])
		Y_train = np.array(Y[:perIndex]).T[0]
		Y_test = np.array(Y[perIndex:]).T[0]
		"""
		X_train = pd.DataFrame(X[:perIndex])
		X_test = pd.DataFrame(X[perIndex:])
		Y_train = pd.DataFrame(Y[:perIndex])
		Y_test = pd.DataFrame(Y[perIndex:])
		"""
		print(len(X_train),len(X_test),len(Y_train),len(Y_test))

		return X_train, X_test, Y_train, Y_test

if __name__ == '__main__':
	with Mysqldb(**mysqlconfig) as db:
		randomForest = RandomForest(db)
		
		X_train, X_test, Y_train, Y_test = randomForest.prepareDataForForrest()
		#randomForest.testIris(X_train, Y_train)
		
		#clf = randomForest.trainRandomForestClassifier(X_train, Y_train)
		pickle_in = open('randomforest.pickle', 'rb')
		clf = pickle.load(pickle_in)

		print(clf.score(X_test,Y_test))
		"""hit = 0
		sum = len(X_test)
		for i, x in enumerate(X_test):
			prediction = np.array(clf.predict(x)[0])
			expected = np.array(Y_test[i])
			if (prediction == expected).all():
				hit = hit + 1
				print("hit")
			#print(x)
			#print("prediction: %s \tactual: %s" % (clf.predict(x), Y_test[i]))
		print(hit/sum)
		#print(clf.predict([0,1, 0]))
		#print(clf.decision_path([0,1,0]))
		"""
		