import numpy as np
import matplotlib.pyplot as plt
from mysqldb import Mysqldb
from config import *

class PlotData():
	"""docstring for ClassName"""
	def __init__(self, db):
		self.db = db
		
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

if __name__ == '__main__':
	with Mysqldb(**mysqlconfig) as db:
		plotData = PlotData(db)
		plotData.plotExample()
