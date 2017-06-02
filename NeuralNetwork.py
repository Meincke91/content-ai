from prepareData import PrepareData
from mysqldb import Mysqldb
from config import *
import numpy as np
import time

class NeuralNetwork():
	"""docstring for ClassName"""

	def fetch_date():
		print()

	def sigmoid(x):
		output = 1/(1+np.exp(-x))
    	return output

	def sigmoid_derivative(output):
    	return output*(1-output)

	def clean_up_sentence(sentence):
		print()	

	def bag_of_words():
		print()

	def think(sentence, show_details=False):
		print()

	def train(X, y, hidden_neurons=10, alpha=1, epochs=50000, dropout=False, dropout_percent=0.5):
		print()

	def test():
		X = np.array(training)
		y = np.array(output)

		start_time = time.time()

		train(X, y, hidden_neurons=20, alpha=0.1, epochs=100000, dropout=False, dropout_percent=0.2)

		elapsed_time = time.time() - start_time
		print ("processing time:", elapsed_time, "seconds")
if __name__ == '__main__':
	prepareData = PrepareData()
	prepareData.removeStopWords(["one"])
		