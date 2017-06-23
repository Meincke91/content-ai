from Mysqldb import Mysqldb
from LinkUtils import LinkUtils
from Webscraper import WebScraper
from PrepareData import PrepareData

from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse
from urllib.parse import urlparse
import re
import operator

from config import *
from medicalTerms import *

class WebCrawler(HTMLParser):
	def __init__(self, db):
		HTMLParser.__init__(self) 
		self.db = db
		self.prepareData = PrepareData(db)

	def on_error(self, status):
		print (self)
		print (status)

	def handle_starttag(self, tag, attrs):
		if tag == 'a':
				for (key, value) in attrs:
					if key == 'href':
						newUrl = parse.urljoin(self.baseUrl, value)
						self.links = self.links + [newUrl]

		if tag == 'script' or tag == 'style' or tag == 'meta' or tag == 'img' or tag == 'svg':
			return

	def handle_data(self, data):
		if data.strip() != "" and len(data.strip()) > 20:
			wordsInData = data.split(" ")
			wordsInData = filter(None, wordsInData) 

			for word in wordsInData:
				wordL = "".join(word.split()).lower()


				if "www" in wordL:
					return
				for char in wordL:
					if char in '=+*/}{()<>@©_':
						return 

					elif not char in 'qwertyuiopasdfghjklzxcvbnm':
						wordL = wordL.replace(char,'')
					

				#for char in '?.!/;:+}{[]"_<>#€%˜$¯”,\'=()*’´`“\\':  
				#   wordL = wordL.replace(char,'')  

				if len(wordL) < 50 and len(wordL) > 0 and (not (wordL == "" or wordL == " " or wordL == "\n" or wordL == "\t" or wordL[0] in '0123456789- –')):
					if not wordL in self.words:
						self.words[wordL]=1
					else:
						self.words[wordL]=self.words[wordL] + 1

	# get links from 
	def scrapeSite(self, url):
		self.links = []
			
		if "twitter" in url or "facebook" in url or "youtube" in url or "instagram" in url or "linkedin" in url:
			return None

		response = None

		try:
			response = urlopen(url, timeout=2)

			if response == None or response.getcode() != 200:
				return None

			self.baseUrl = response.geturl()

			if len(self.baseUrl) > 512:
				return None
			if self.baseUrl != url:
				linkId, newDomainId = self.db.selectLink(self.baseUrl)

				# if new link already exists
				if linkId != None:

					# get old link id, domain_id and domain_relation_ids
					oldLinkId, oldDomainId = self.db.selectLink(url)
					oldRelatedDomainIds = self.db.selectRelatedFromBase(oldLinkId)

					# if domain relations exist
					if oldRelatedDomainIds != None:
						for oldRelatedDomainId in oldRelatedDomainIds:

							newToOldRelation = self.db.selectDomainRelationId(newDomainId, oldRelatedDomainId)

							if newToOldRelation == None:
								# If no relation exist set base_relation_id = new domain id
								self.db.updateLinkRelationBase(oldRelatedDomainId, newDomainId)
							else: 
								# if there exist a domain relation between actual domain and proxy relations
								count = selectDomainRelationCount(newToOldRelation)
								if count > 0:
									self.db.updateLinkRelation(newToOldRelation, count)

								# delete existing domain relation
								self.db.deleteDomainRelation(oldRelatedDomainId)
								print("deleting domain relation record with id %s - url: %s" % (oldRelatedDomainId, url))
				else:
					# replace existing link
					self.db.updateLink(self.baseUrl, url)

			if 'text/html' in response.getheader('Content-Type'):

				htmlBytes = response.read()

				htmlString = htmlBytes.decode("utf-8")

				self.feed(htmlString)
				return self.links
			else:
				return None
		except Exception as e:
			print(e)
			return None

	def updateRelations(self, newUrl, oldUrl):
		print()


	def tfidfSpider(self, keywords, top_ranked=3, max_iterations=200000):
		current_iteration = 0

		while current_iteration < max_iterations:
			current_iteration = current_iteration + 1

			tfidfs = self.prepareData.calculateTFIDFs(keywords)
			sorted_tfidfs = sorted(tfidfs.items(), key=operator.itemgetter(1))[-top_ranked:]

			for article_id in sorted_tfidfs:
				domain_id = self.db.selectDomainFromArticle(article_id[0])
				print(article_id)
				# social media sites
				blackListDomainIds = [27600, 27640, 27658, 27697, 27714, 27859, 27889, 27887, 27888, 27947, 27958, 27966, 27969]
				if not domain_id in blackListDomainIds:
					relatedDomains = self.db.selectRelatedFromBase(domain_id)
					if (not relatedDomains is None) and len(relatedDomains) > 0:
						links_dict = self.db.selectDomainLinksFromIds(relatedDomains)
						for baseLinkId, url in links_dict.items():
							self.db.updateCrawledLink(baseLinkId)
							baseDomainId = self.db.selectOnlyDomainFromId(baseLinkId)
							self.words = {}
							links = self.scrapeSite(url)
							articleId = self.db.insertArticle(baseLinkId)

							for key, value in self.words.items():
								wordId = self.db.selectWord(key)
								if wordId == None:
									wordId = self.db.insertWord(key, value)
								else:
									self.db.updateWord(wordId, value)

								self.db.insertArticleWord(articleId, wordId, value)
							if(links != None and len(links) > 0):

								self.insertLinks(baseDomainId, links) 


	def weightedSpider(self, maxLinks=10000):
		webscraper = WebScraper()
		links = []
		self.words = {}

		numberVisited = 0

		while numberVisited < maxLinks:
			numberVisited = numberVisited + 1
			domainId = self.db.selectDomainFromHighestRelatedTFIDF()
			baseLinkId, url = self.db.selectDomainLinks(domainId)

			self.db.updateCrawledLink(baseLinkId)
			# print("%s %s %s " % (baseLinkId, url, domainId))
			try:
				self.words = {}
				links = self.scrapeSite(url)
				articleId = self.db.insertArticle(baseLinkId)

				for key, value in self.words.items():
					wordId = self.db.selectWord(key)
					if wordId == None:
						wordId = self.db.insertWord(key, value)
					else:
						self.db.updateWord(wordId, value)

					self.db.insertArticleWord(articleId, wordId, value)
				if(links != None and len(links) > 0):
					self.insertLinks(domainId, links) 

			except Exception as e:
				print("error spider2: %s " % (e))

	#def findAndInsertTFIDF(self, wordId, articleId, wordId):
	#	insertArticleTFIDF

	def spider(self, maxLinks=10000):
		webScraper = WebScraper()
		links = []
		self.words = {}

		numberVisited = 0

		while numberVisited < maxLinks:
			numberVisited = numberVisited + 1

			baseLinkId, url, domainId = self.db.selectUncrawledLinks()
			self.db.updateCrawledLink(baseLinkId)
			# print("%s %s %s " % (baseLinkId, url, domainId))
			try:
				self.words = {}
				links = self.scrapeSite(url)
				articleId = self.db.insertArticle(baseLinkId)

				print(url)

				for key, value in self.words.items():
					wordId = self.db.selectWord(key)
					if wordId == None:
						wordId = self.db.insertWord(key, value)
					else:
						self.db.updateWord(wordId, value)

					self.db.insertArticleWord(articleId, wordId, value)
				if(links != None and len(links) > 0):
					self.insertLinks(domainId, links) 

			except Exception as e:
				print("error spider2: %s " % (e))

			
			#print("done with links")

	def spiderList(self, maxLinks=10000):
		webScraper = WebScraper()
		links = self.db.selectUncrawledLinkList(maxLinks)
		self.words = {}

		for baseLinkId, value in links.items():
			url = value[0]
			domainId = value[1]

			print("%s %s %s " % (baseLinkId, url, domainId))
			try:
				self.db.updateCrawledLink(baseLinkId)
				self.words = {}
				links = self.scrapeSite(url)
				articleId = self.db.insertArticle(baseLinkId)

				print(url)

				for key, value in self.words.items():
					wordId = self.db.selectWord(key)
					if wordId == None:
						wordId = self.db.insertWord(key, value)
					else:
						self.db.updateWord(wordId, value)

					self.db.insertArticleWord(articleId, wordId, value)
				if(links != None and len(links) > 0):
					self.insertLinks(domainId, links) 

			except Exception as e:
				print("error spider2: %s " % (e))

	def domainSpider(self, keywords):
		webScraper = WebScraper()
		links = []
		self.words = {}

		domainIds = self.db.selectDomainIdsFromKeywords(keywords)

		domainLinks = self.db.selectLinkFromDomain(domainIds)

		for linkId, url in domainLinks.items():
			self.db.updateCrawledLink(linkId)
			links = self.scrapeSite(url)

			articleId = self.db.insertArticle(linkId)

			print(url)
			for key, value in self.words.items():

				wordId = self.db.selectWord(key)
				if wordId == None:
					wordId = self.db.insertWord(key, value)
				else:
					self.db.updateWord(wordId, value)

				self.db.insertArticleWord(articleId, wordId, value)

			
			if(links != None and len(links) > 0):
				domainId = self.db.selectDomainFromLink(linkId)

				self.insertLinks(domainId, links) 

			

	# insert all links collected
	def insertLinks(self, baseDomainId, links):
		

		for link in links:
			if link != None and len(link) != 0 and len(link) <= 512:
				linkId, domainId = self.db.selectLink(link)

				if linkId == None:
					linkUtils = LinkUtils()
					domain, domainExtension = linkUtils.linkSplitter(link) 
					if domain != None and domainExtension != None:
						linkId = self.db.insertLink(link, domain, domainExtension)
						domainId = self.db.selectDomainFromLink(linkId)

				# insert into domain relation
				if domainId != None and baseDomainId != domainId:
					self.db.insertOrUpdateLinkRelation(baseDomainId, domainId)
			
	def insertDomainExtensions(self):
		self.db.insertDomainExtensions()
if __name__ == '__main__':
	#with urlopen('http://bit.ly/yk3b9m') as f:
		#print(f.read(1000).decode('utf-8'))


	with Mysqldb(**mysqlconfig) as db:
		webCrawler = WebCrawler(db)
		#ebCrawler.insertDomainExtensions()
		webCrawler.tfidfSpider()
		

		#html, links = linkParser.getLinks('http://bit.ly/yk3b9m')

		