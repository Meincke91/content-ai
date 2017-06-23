from PrepareData import PrepareData
from Mysqldb import Mysqldb

import numpy as np
import time
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

from config import *

class NeuralNetwork():
	"""docstring for ClassName"""
	def __init__(self, db):
		self.prepareData = PrepareData(db)

	def train(self):
		mnist = input_data.read_data_sets("/tmp/data/", one_hot = True)
		n_nodes_hl1 = 500
		n_nodes_hl2 = 500
		n_nodes_hl3 = 500
		n_classes = 10
		batch_size = 100

		x = tf.placeholder('float', [None, 784])
		y = tf.placeholder('float')

		l1 = tf.add(tf.matmul(data,hidden_1_layer['weights']), hidden_1_layer['biases'])
		l1 = tf.nn.relu(l1)

		l2 = tf.add(tf.matmul(l1,hidden_2_layer['weights']), hidden_2_layer['biases'])
		l2 = tf.nn.relu(l2)

		l3 = tf.add(tf.matmul(l2,hidden_3_layer['weights']), hidden_3_layer['biases'])
		l3 = tf.nn.relu(l3)

		output = tf.matmul(l3,output_layer['weights']) + output_layer['biases']

		return output

	def neural_network_model(data):
		hidden_1_layer = {'weights':tf.Variable(tf.random_normal([784, n_nodes_hl1])),
						  'biases':tf.Variable(tf.random_normal([n_nodes_hl1]))}

		hidden_2_layer = {'weights':tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
						  'biases':tf.Variable(tf.random_normal([n_nodes_hl2]))}

		hidden_3_layer = {'weights':tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
						  'biases':tf.Variable(tf.random_normal([n_nodes_hl3]))}

		output_layer = {'weights':tf.Variable(tf.random_normal([n_nodes_hl3, n_classes])),
						'biases':tf.Variable(tf.random_normal([n_classes]))}

	def train_neural_network(x):
		prediction = neural_network_model(x)
		cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=y) )
		
if __name__ == '__main__':
	with Mysqldb(**mysqlconfig) as db:
		neuralNetwork = NeuralNetwork(db)
		