from domainExtensions import *

class LinkUtils:
	def domainExtension(self):
		crimefile = open('domainExtensions.txt', 'r')
		yourResult = [line.split(',') for line in crimefile.readlines()]
		f = open('workfile.', 'w')
		for line in yourResult:
			f.write('"%s",' % (line))
		print(len(yourResult))

	def linkSplitter(self, link):
		try:
			if link == None or link == "" or not "//" in link or "mailto:" in link:
				return None, None

			domain_t = link.split('//')[1]
			if "/" in domain_t:
				domain_t = domain_t.split('/')[0]

			if 'www.' in domain_t:
				domain_t = domain_t.split('www.')[1]

			domain_extension = domain_t.split('.')[-1]
			domain = ".".join(domain_t.split('.')[:-1])
			if domain_extension.upper() in domainExtensions:
				return domain.lower(), domain_extension.lower()
				
			return None, None
		except:
			print("error splitting link")
		


	def extendLink(self, url):
		if not "www" in url:
			tmp_url = url.split("://")
			return "://www.".join(tmp_url)
		return url

		"""domain_t = link.split('//')[1].split('/')[0]
		domainWWW = domain_t.split('www.')
		if len(domainWWW) > 1:
			domain = domainWWW[1]
		else:
			domain = domain_t.split('.')[0]
		
		domain_name = link.split('.')[-1].split('/')[0]
		print("%s \n domain: %s  domain_name:%s" % (link, domain, domain_name))"""