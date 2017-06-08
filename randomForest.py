from sklearn.ensemble import RandomForestClassifier
from mysqldb import Mysqldb
from config import *
from prepareData import PrepareData
import numpy as np

class RandomForest():
	"""docstring for ClassName"""
	def __init__(self):
		pass

	def randomForestClassifier(self, X, Y):
		
		
		clf = RandomForestClassifier(n_estimators=10)
		clf = clf.fit(X, Y)

		
		return clf

if __name__ == '__main__':
	with Mysqldb(**mysqlconfig) as db:
		randomForest = RandomForest()
		prepareData = PrepareData(db)

		documents, classes, words = prepareData.getTrainingDocuments(prepareData.dummyData())
		X, Y = prepareData.training_set(documents, classes, words)
		print("len x: %s,  len y: %s " % (len(X), len(Y)))
		per = 90
		perIndex = int(len(X)*(80/100))

		X_train = X[:perIndex]
		X_test = X[perIndex:]
		Y_train = Y[:perIndex]
		Y_test = Y[perIndex:]

		clf = randomForest.randomForestClassifier(X_train, Y_train)
		
		

		hit = 0
		sum = len(X_test)
		for i, x in enumerate(X_test):
			prediction = np.array(clf.predict(x)[0])
			expected = np.array(Y_test[i])
			if (prediction == expected).all():
				hit = hit + 1
				print("hit")
			print(x)
			print("prediction: %s \tactual: %s" % (clf.predict(x), Y_test[i]))
		print(hit/sum)
		#print(clf.predict([0,1, 0]))
		#print(clf.decision_path([0,1,0]))