from Mysqldb import Mysqldb
from LinkUtils import LinkUtils

from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse

from config import *

class WebScraper(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self) 

	def on_error(self, status):
		print (self)
		print (status)

	def findBlockOfText(self, data):
		bodyContainer = data.split("<body>")
		print(len(bodyContainer))

	#def handle_starttag(self, tag, attrs):
		if tag == 'body':
			print("Encountered a body tag: %s" % (attrs))

	#def handle_endtag(self, tag):
		#print("Encountered an end tag: %s" % (tag))

	def handle_data(self, data):
		
		if data.strip() != "" and len(data.strip()) > 20:
			wordsInData = data.split(" ")
			for word in wordsInData:
				if (not word.isspace()) and not (word == " " or word == "\n" or word == "\t"):
					if not word in self.words:
						self.words[word]=1
					else:
						self.words[word]=self.words[word] + 1
				
				#print("Encountered data: %s" % (data))

	def testStripper(self, url):
		self.words = {}
		try:
			response = urlopen(url, timeout=2)
		except Exception as e:
			print(e)
			return None

		if response != None or response.getcode() == 200:
			if 'text/html' in response.getheader('Content-Type'):

				htmlBytes = response.read()

				htmlString = htmlBytes.decode("utf-8")
				
				self.feed(htmlString)
				return self.words
			else:
				return None


if __name__ == '__main__':
	#with urlopen('http://bit.ly/yk3b9m') as f:
		#print(f.read(1000).decode('utf-8'))


	
	WebScraper = WebScraper()
	WebScraper.testStripper("http://www.abc.net.au/news/2016-08-11/life-after-a-cancer-diagnosis/7701152")