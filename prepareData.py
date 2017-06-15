from mysqldb import Mysqldb
from config import *
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import operator
from math import log2
from medicalTerms import *
from blacklist import *

class PrepareData():
	"""docstring for ClassName"""
	def __init__(self, db):
		self.db = db
		self.stemmer = LancasterStemmer()
	
	def NLTKremoveStopWords(self, words):
		stop_words = set(stopwords.words('english'))

		outputWords = []

		for word in words:
			if not word in stop_words:
				outputWords.append(word)
		return outputWords

	def NLTKremoveStopWordsFromDict(self, inputWords):
		stop_words = set(stopwords.words('english'))

		outputWords = {}

		for word, value in inputWords.items():
			if not word in stop_words:
				outputWords[word] = value
		return outputWords


	def removeStopWordsFromDict(self, inputWords):
		stop_words = self.db.selectWordsInRange(0,10)

		outputWords = {}
		for word, value in inputWords.items():
			if not word in stop_words:
				outputWords[word] = value

		return outputWords

	def stemWords(self, words):
		ignore_words = set(stopwords.words('english'))
		# stem and lower each word and remove duplicates
		words = [self.stemmer.stem(str(w).lower()) for w in words if w not in ignore_words]
		words = list(set(words))
		return words

	def getTrainingDocuments(self, training_data):
		words = []
		classes = []
		documents = []
		
		# loop through each sentence in our training data
		for pattern in training_data:
			# tokenize each word in the sentence
			w = pattern['document']
			# add to our words list
			words.extend(w)
			# add to documents in our corpus
			documents.append((w, pattern['class']))
			# add to our classes list
			if pattern['class'] not in classes:
				classes.append(pattern['class'])

		words = self.stemWords(words)

		# remove duplicates
		classes = list(set(classes))

		"""
		print (len(documents), "documents")
		print (len(classes), "classes", classes)
		print (len(words), "unique stemmed words", words)
		"""
		return documents, classes, words



	def bag_of_words(self, document, words, print_details=False):
		bag = [0]*len(words)

		for d_word in document:
			for i, w in enumerate(words):
				if w == d_word:
					bag[i] = 1
					if print_details:
						print("found in bag: %s" % w)

		return np.array(bag)

	def training_set(self, documents, classes, words):
		training = []
		output = []
		# create an empty array for our output
		output_empty = [0] * len(classes)

		for document in documents:
			
			bag = []

			pattern_words = document[0]
			pattern_words = self.stemWords(pattern_words)

			for w in words:
				if w in pattern_words:
					bag.append(1)
				else:
					bag.append(0)
			
			training.append(bag)

			# create output
			output_row = list(output_empty)
			output_row[classes.index(document[1])] = 1
			output.append(output_row)

		return training, output

	def dummyData(self):
		training_data = []
		training_data.append({"class":"medical", "document":["cancer", "pancreatic", "medicine"]})
		training_data.append({"class":"spam", "document":["is", "your", "day"]})
		training_data.append({"class":"spam", "document":["good", "day"]})
		training_data.append({"class":"medical", "document":["menigitis", "is", "medicine", "going", "cancer"]})
		training_data.append({"class":"spam", "document":["how", "going", "today"]})
		training_data.append({"class":"spam", "document":["tomorrow", "it", "going", "today"]})
		training_data.append({"class":"medical", "document":["medicine", "menigitis", "it", "going", "today"]})
		training_data.append({"class":"spam", "document":[ "is", "it"]})
		training_data.append({"class":"spam", "document":["how", "is", "it", "going", "today"]})
		training_data.append({"class":"medical", "document":["pancreatic", "cancer", "menigitis", "medicine"]})
		training_data.append({"class":"spam", "document":["menigitis", "cancer"]})
		training_data.append({"class":"spam", "document":["good", "medicine", "it", "cancer"]})
		training_data.append({"class":"spam", "document":["today"]})
		training_data.append({"class":"medical", "document":["menigitis", "menigitis", "cancer"]})
		training_data.append({"class":"medical", "document":["pancreatic", "cancer", "medicine"]})
		training_data.append({"class":"spam", "document":["today", "are"]})

		print ("%s sentences in training data" % len(training_data))
		return training_data

	def getRealData(self, batchSize=1000, batches=1000):
		training_data = []

		currentBatch = 0
		while currentBatch < batches:
			articles = self.db.selectArticlesWithClass([0,1], limitLow=batchSize*currentBatch, batchSize=batchSize)

			currentBatch = currentBatch + 1
			if len(articles) < batchSize:
				currentBatch = batches

			for articleId, articleClass in articles.items():

				training_data.append({"class":articleClass, "document":self.db.selectWordsFromArticle(articleId)})
			print("batch %s done. with batch-size of: %s. First id: %s. Total length of data: %s" % (currentBatch, batchSize, articleId, len(training_data)))
		return training_data

	def getCompleteData(self):
		documents, classes, words = self.getTrainingDocuments(prepareData.getRealData())
		X, Y = self.training_set(documents, classes, words)
		return X, Y

	def findArticlesFromKeywords(self, keywords):
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

		
		topicWords = self.NLTKremoveStopWordsFromDict(collectiveWords)
		sorted_x = sorted(topicWords.items(), key=operator.itemgetter(1))

		for x in sorted_x[int(len(sorted_x)*0.95):]:
			print("%s, %s" % (self.db.selectWordFromId(x[0]), x[1]))

	def estimateMedicalWebsites(self, maxBatches=1000, batchSize=100):
		currentCount = 0
		while maxBatches > currentCount:
			articleIds = self.db.selectArticleWithNoTFIDF(batchSize)
			print(articleIds)
			for articleId in articleIds:
				#linkId = self.db.selectLinkFromArticle(articleId)
				#linkStr = self.db.selectLinkStr(linkId)
				#print(linkStr)
				#if self.isLinkRelevant(linkStr, linkId):
				TFIDF = self.calculateTDIDF(medicalTerms, articleId)
				lix = self.calculateLix(articleId)

				self.db.updateArticleTFIDF(articleId, TFIDF)
				self.db.updateArticleLix(articleId, lix)

			currentCount = currentCount + 1
		"""	
		sorted_tfidfs = sorted(tfidfs.items(), key=operator.itemgetter(1))

		for s_tdidf in sorted_tfidfs:
			print(s_tdidf)
			#print("link: %s\nkeywords: %s\ttf.idf: %s" % (self.db.selectLinkStrFromArticle(s_tdidf[0]), medicalTerms, s_tdidf))
		"""
		print("done")

	def estimateArticleClass(self):
		# estimate class based on tfidf being higher than domain average, and in the top 95 percent of all tfidf values
		articleTfidfAndLix = self.db.selectArticlTfidfAndLix(100000)
		tfidfValue, LixValue = self.getPercentageTfidfAndLixValue(articleTfidfAndLix, 90)
		
		for key, value in articleTfidfAndLix.items():
			avgDomainTfidf, avgDomainLix = self.db.selectDomainTfidfAndLixFromArticle(key)
			
			if(value[0]-avgDomainTfidf > 0.0 and value[0] > tfidfValue):
				self.db.updateArticleClass(key, 1)
			else:
				self.db.updateArticleClass(key, 0)
		
	def getPercentageTfidfAndLixValue(self, dictionary, percentage):
		tfidfs = []
		lix = []

			#lix = dictionary.values()(1)
		for key, value in dictionary.items():
			tfidfs.append(value[0])
			lix.append(value[1])
		index = int(len(tfidfs)*(percentage/100))

		tfidfValue = sorted(tfidfs)[index]
		LixValue = sorted(lix)[index]

		return tfidfValue, LixValue 

	def calculateAverageDomainStats(self):
		articleAndDomains = self.db.selectArticleAndDomain(100000)
		domainAverages = {}
		for key, value in articleAndDomains.items():
			if not value[2] is None and value[2] > 0.0: 
				domainId = value[0]
				if not domainId in domainAverages:
					domainAverages[domainId] = [value[2], value[3], 1]
				else:
					prevTFIDFsum = domainAverages[domainId][0]
					prevLixsum = domainAverages[domainId][1]
					prevCount = domainAverages[domainId][2]
					domainAverages[domainId] = [prevTFIDFsum + value[2], prevLixsum + value[3], prevCount + 1]
					#print("id: %s \tdomain: %s\t\ttfidf: %s\tlix: %s" % (key, domainAndExtension, value[2], value[3]))
		
		

		for key, value in domainAverages.items():
			self.db.updateDomainTFIDF(key, value[0]/value[2])
			self.db.updateDomainLix(key, value[1]/value[2])
			#domainAverages[key] = [value[0]/value[2], value[1]/value[2], value[2]]
			#print("%s\ntfidf: %s\tlix: %s" % (key, value[0]/value[2], value[1]/value[2]))

		#sortedDomainAverages = sorted(domainAverages.items(), key=lambda i: i[1][0])
		#for key, value in sortedDomainAverages:
		#	print("%s\ntfidf: %s\tlix: %s" % (key, value[0], value[1]))
			
		
	def calculateLix(self, articleId):
		wordIds = self.db.selectWordsFromArticle(articleId)
		
		wordSum = 0
		wordCount = 0
		lix = 0

		for wordId, count in wordIds.items():
			word = self.db.selectWordFromId(wordId)
			wordCount = wordCount + count
			wordSum = wordSum + (len(str(word)) * count)

		if wordCount > 0:
			lix = wordSum/wordCount

		return lix

	def calculateTDIDF(self, keywords, articleId=None):
		print("calculateTDIDF %s " % (articleId))
		wordIds = []
		TFIDF = 0
		for keyword in keywords:
			wordIds.append(self.db.selectWord(keyword.lower()))

		wordIds = self.removeNoneFromArray(wordIds)

		articleIds = self.db.selectArticleFromWords(wordIds)

		N = self.db.selectArticleSize()

		IDF = log2(N/len(articleIds))

		if articleId is None:
			articleId = articleIds[0]

		words = self.db.selectWordsFromArticle(articleId)

		baseWordCount = 0

		for wordId, count in words.items():
			if wordId in wordIds:
				baseWordCount = baseWordCount + words[wordId]
			

		words = self.NLTKremoveStopWordsFromDict(words)

		# even if stopword calculate the TD.IDF
		#if not wordId in words or words[wordId] is None:
		#	words[wordId] = baseWordCount

		maxWordLength = self.getMaximumValueFromDict(words)
		#sorted_x = sorted(words.items(), key=operator.itemgetter(1))
		if maxWordLength > 0:
			TF = baseWordCount / maxWordLength
			TFIDF = TF * IDF
		return TFIDF

	def getMaximumValueFromDict(self, dictionary):
		print("getMaximumValueFromDict %s" % (len(dictionary)))
		maxValue = 0
		for key, value in dictionary.items():
			print(value)
			if value > maxValue:
				maxValue = value
		return maxValue

	def removeNoneFromArray(self, array):
		newArray = []
		for element in array:
			if element != None:
				newArray.append(element)
		return newArray

	def isLinkRelevant(self, linkStr, linkId):		
		
		for blword in blacklistedLinkWords:
			if not blword in linkStr:
				domainId = self.db.selectDomainFromLink(linkId)
				domain, extension = self.db.selectDomain(domainId)
				if not domain in blacklistedDomains:
					return True
		return False
	def asdsad():
		 ".".join((row['domain_name'], row['extension']))

if __name__ == '__main__':
	with Mysqldb(**mysqlconfig) as db:
		prepareData = PrepareData(db)
		prepareData.estimateMedicalWebsites(batchSize=100)
		#prepareData.getRealData()
		#print(prepareData.calculateTDIDF(medicalTerms))

			#,"Anthrax", "Atypical", "mycobacteriosis", "familial", "Balantidiasis", "Brucellosis", "Bubonic plague", "Buruli ulcer", "Cat scratch disease", "Chancroid", "Cholera", "Clostridium sordellii infection", "Cutaneous anthrax","Glanders"] )
		
		#print(prepareData.bag_of_words())