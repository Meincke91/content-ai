from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse
from urllib.parse import urlparse
from mysqldb import Mysqldb
from linkUtils import LinkUtils
from webscraper import WebScraper
from config import *
import re

class LinkParser(HTMLParser):
	def __init__(self, db):
		HTMLParser.__init__(self) 
		self.db = db

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
				#	wordL = wordL.replace(char,'')  

				if len(wordL) < 50 and len(wordL) > 0 and (not (wordL == "" or wordL == " " or wordL == "\n" or wordL == "\t" or wordL[0] in '0123456789- –')):
					if not wordL in self.words:
						self.words[wordL]=1
					else:
						self.words[wordL]=self.words[wordL] + 1

	# get links from 
	def scrapeSite(self, url):
		self.links = []
			
		if "twitter" in url or "facebook" in url or "youtube" in url or "instagram" in url:
			return None

		response = None

		try:
			response = urlopen(url, timeout=2)
			if response == None or response.getcode() != 200:
				return None

			self.baseUrl = response.geturl()
			if len(self.baseUrl) < 512:
				return None
			if self.baseUrl != url:
				print("baseUrl: %s" % (self.baseUrl))
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


							print(domainRelation)

					#print(domainRelations)
					# update reference
					# update domain_relation
						# select where base_domain_id = old_domain
							# for all where base_domain_id = new_domain_id and related_domain_id = old_related_domain_id
							# if record exist, update with old_count
							# else create with new_domain_id, old_related_domain_id and old_count
					# update article link
						# for all where link_id = old_link_id SET = new_link_id 
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
		

	def spider2(self, maxLinks=10000):
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

	def domainSpider(self, keywords, maxLinks=10000 ):
		webScraper = WebScraper()
		links = []
		self.words = {}

		numberVisited = 0
		domainIds = self.db.selectDomainIdsFromKeywords(keywords)

		domainLinks = self.db.selectLinkFromDomain(domainIds)

		while numberVisited < maxLinks:
			numberVisited = numberVisited + 1

			for linkId, url in domainLinks.items():
				self.db.updateCrawledLink(linkId)


				self.words = {}
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
		linkUtils = LinkUtils()

		for link in links:
			if link != None and len(link) != 0 and len(link) <= 512:
				linkId, domainId = self.db.selectLink(link)

				if linkId == None:
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
		linkParser = LinkParser(db)
		#linkParser.insertDomainExtensions()
		linkParser.domainSpider(['leukemia'])
		

		#html, links = linkParser.getLinks('http://bit.ly/yk3b9m')

		