import pymysql.cursors
from domainExtensions import *
from linkUtils import LinkUtils
# Maybe this could be done easier with coroutines?


class Mysqldb:
    def __init__(self, host, user, password, db):
        """Create an object that connects and inserts rows to mysql

        Args:
            host (string): The database host
            user (string): Username for accessing the database
            password (string): Password for the database
            db (string): The database/schema name
        """
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'db': db,
            'port': 3306,
            'cursorclass': pymysql.cursors.DictCursor
        }

    def __enter__(self):
        """Initialize the connection"""
        self.connection = pymysql.connect(**self.config)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the connection to the database

        This method is called by the context manager when the context
        manager is exited for any reason.
        """
        self.connection.close()

    def insertTweet(self, userId, tweet, links):
        if userId == None or None in links:
            return None

        tweetId = None
        try:
            with self.connection.cursor() as cursor:

                # Select tweet with id
                selectSQL = "SELECT id FROM tweets WHERE id_str = %s"
                cursor.execute(selectSQL, (tweet['id_str']))

                tweetId = None
                for row in cursor:
                    tweetId = row['id']
                # Insert tweet if non existing
                if tweetId == None:  
                    sql = "INSERT INTO `tweets` (`user_id`, `id_str`, `text`, `lang`, `created_at`) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (userId, tweet['id_str'], tweet['text'].encode('ascii', 'ignore'), tweet['lang'], tweet['created_at']))
                    tweetId = cursor.lastrowid

                # insert all link tweet relations
                for linkId in links:
                    tweet_link_sql = "INSERT INTO tweet_link (`tweet_id`,`link_id`) VALUES (%s, %s)"
                    cursor.execute(tweet_link_sql, (tweetId, linkId))
        except:
            print("insert tweet error %s" % (cursor._last_executed))

        self.connection.commit()

    def insertUser(self, tweet):

        userId = None
        if 'user' in  tweet and 'id_str' in tweet['user']: 
            try:
                with self.connection.cursor() as cursor:
                    selectSQL = "SELECT id from user WHERE id_str = %s"
                    cursor.execute(selectSQL, (tweet['user']['id_str']))
                    userId = None
                    for row in cursor:
                        userId = row['id']

                    if userId == None and 'user' in tweet:
                        sql = "INSERT INTO `user` (`created_at`, `id_str`, `favourites_count`, `verified`,`followers_count`,`friends_count`,`statuses_count`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        cursor.execute(sql, (tweet['user']['created_at'], tweet['user']['id_str'], tweet['user']['favourites_count'], tweet['user']['verified'], tweet['user']['followers_count'], tweet['user']['friends_count'], tweet['user']['statuses_count']))

                        userId = cursor.lastrowid

                    cursor.close()
                    
            except:
                print("insert user error")
            
            self.connection.commit()

        return userId

        # insert into the link table

    ############
    #   LINK
    ############    

    def insertLink(self, link, domain, domainExtension):

        try:
            with self.connection.cursor() as cursor:
                selectSQL = "SELECT id FROM link WHERE link_str = %s"
                cursor.execute(selectSQL, (link))
                linkId = None
                for row in cursor:
                    linkId = row['id']
                
                if linkId == None:
                    domainExtensionId = self.selectDomainExtensionId(domainExtension)
                    if domainExtensionId != None:
                        domainId = self.selectDomainId(domain, domainExtensionId)

                        if domainId == None:
                            domainId = self.insertDomain(domain, domainExtensionId)

                        if domainId != None:
                        
                            insertLinkSQL = "INSERT INTO `link` (`link_str`, `domain_id`) VALUES (%s, %s)"
                            cursor.execute(insertLinkSQL, (link, domainId))
                            linkId = cursor.lastrowid

                cursor.close()

                self.connection.commit()

                return linkId

        except:
            print("insert link error: %s " % (cursor._last_executed) )

        return None

    def selectLink(self, url):
        selectSQL = "SELECT id, domain_id FROM link WHERE link_str = %s"
        linkId = None
        domainId = None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (url))
                for row in cursor:
                    linkId = row['id']
                    domainId = row['domain_id']
                cursor.close()
        except:
            print("Select domain id error %s " % (cursor._last_executed))
            
        return linkId, domainId

    def updateLink(self, link, oldLink):
        linkUtils = LinkUtils()
        domain, domainExtension = linkUtils.linkSplitter(link) 
        if link == None or len(link) == 0 or domain == None or domainExtension == None:
            return None

        try:
            with self.connection.cursor() as cursor:
                selectSQL = "SELECT id FROM link WHERE link_str = %s"
                cursor.execute(selectSQL, (oldLink))
                linkId = None
                for row in cursor:
                    linkId = row['id']

                if linkId != None:
                    domainExtensionId = self.selectDomainExtensionId(domainExtension)
                    if domainExtensionId != None:
                        domainId = self.selectDomainId(domain, domainExtensionId)

                        if domainId == None:
                            domainId = self.insertDomain(domain, domainExtensionId)

                        if domainId != None:
                            updateSQL = "UPDATE link SET link_str = %s, domain_id = %s WHERE id=%s"
                            cursor.execute(updateSQL, (link, domainId, linkId))
                            linkId = cursor.lastrowid

                cursor.close()

                self.connection.commit()

                return linkId

        except:
            print("update link error: %s " % (cursor._last_executed) )

        return None

    def selectLinkFromDomain(self, domainIds):
        selectSQL = "SELECT id, link_str from link WHERE crawled = 0 and domain_id in (%s)"
        in_p=', '.join(list(map(lambda x: '%s', domainIds)))
        selectSQL = selectSQL % in_p
        links = {}

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (domainIds))
                for row in cursor:
                    links[row['id']] = row['link_str']

                cursor.close()
        except: 
            print("error selecting links from domain %s " % (cursor._last_executed))

        return links

    def updateCrawledLink(self, linkId):
        updateSQL = "UPDATE link SET crawled = 1 WHERE id=%s"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(updateSQL, (linkId))
                cursor.close()
        except:
            print("error updating link crawled")

        self.connection.commit()

    def selectUncrawledLinks(self, limit=1, domainId = None):
        if domainId == None:
            selectSQL = "SELECT id, link_str, domain_id FROM `link` WHERE `crawled` = 0 LIMIT %s"
        else:
            selectSQL = "SELECT id, link_str FROM `link` WHERE `crawled` = 0 and domain_id = %s LIMIT %s"


        linkId = None
        linkStr = None

        try:
            with self.connection.cursor() as cursor:
                if domainId == None:
                    cursor.execute(selectSQL, (limit))
                else:
                     cursor.execute(selectSQL, (domainId, limit))

                for row in cursor:
                    linkId = row['id']
                    linkStr = row['link_str']
                    domainId = row['domain_id']

                cursor.close()
        except: 
            print("error selecting domain relation id")

        return linkId, linkStr, domainId

    def selectDomainLinks(self, limit=1):
        selectSQL = "SELECT id, link_str FROM `link` WHERE `crawled` = 0 and domain_id = %s LIMIT %s"
        linkId = None
        linkStr = None
        domainId = None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (limit))
                for row in cursor:
                    linkId = row['id']
                    linkStr = row['link_str']
                    domainId = row['domain_id']

                cursor.close()
        except: 
            print("error selecting domain relation id %s " % (cursor._last_executed))

        return linkId, linkStr, domainId
    # def updateLinkReferences(self, )


    ########
    # DOMAIN
    ########

    def insertDomain(self, domain, domainExtensionId):
        insertSQL = "INSERT INTO `domain` (`domain_name`,`domain_extension_id`) VALUES (%s, %s)"
        domainId = None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insertSQL, (domain, domainExtensionId))
                domainId = cursor.lastrowid

                cursor.close()
        except:
            print("insert domain error %s " % (cursor._last_executed))

        self.connection.commit()

        return domainId

    def selectDomainId(self, domain, domainExtensionId):
        selectSQL = "SELECT id FROM domain WHERE domain_name = %s AND domain_extension_id = %s"
        domainId = None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (domain, domainExtensionId))
                domainId = None
                for row in cursor:
                    domainId = row['id']
                cursor.close()
        except:
            print("Select domain id error %s " % (cursor._last_executed))
            
        return domainId

    def selectDomainFromId(self, linkId):
        selectSQL = "SELECT link.domain, domain_extension.extension FROM link INNER JOIN domain_extension ON link.domain_extension_id=domain_extension.id WHERE link.id = %s"
        domain, extension = None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (linkId))

                for row in cursor:
                    domain = row['domain']
                    extension = row['extension']
        except:
            print("error selecting domain from id")

        return domain, extension

    def selectDomainFromLink(self, linkId):
        selectSQL = "SELECT domain_id FROM link WHERE id = %s"
        domainId = None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (linkId))

                for row in cursor:
                    domainId = row['domain_id']

                cursor.close()
        except Exception as e:
            print("error selecting domain from link id : %s" % (e))

        return domainId

    def selectDomainIdsFromKeywords(self, keywords):
        
        if len(keywords) > 1:
            selectSQL = "SELECT * FROM domain WHERE id in (SELECT domain_id FROM link WHERE id in (SELECT link_id FROM article WHERE id in (SELECT article_id FROM article_word WHERE word_id in (SELECT id from word WHERE word in (%s)))));"
            in_p=', '.join(list(map(lambda x: '%s', keywords)))
            selectSQL = selectSQL % in_p
        else:
            selectSQL = "SELECT * FROM domain WHERE id in (SELECT domain_id FROM link WHERE id in (SELECT link_id FROM article WHERE id in (SELECT article_id FROM article_word WHERE word_id = (SELECT id from word WHERE word = %s))));"

        domainIds = []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (keywords))
                for row in cursor:
                    domainIds.append(row['id'])
                cursor.close()
        except: 
            print("error selecting domain relation id %s " % (cursor._last_executed))

        return domainIds

    ######
    # DOMAIN_EXTENSION
    ####### 
    def insertDomainExtensions(self):
        # Used in the initial setup of the domain_extension table
        sql = "INSERT INTO `domain_extension` (`extension`) VALUES (%s)"
        
        try:
            with self.connection.cursor() as cursor:
                for domain in domainExtensions:
                    cursor.execute(sql, (domain))
                cursor.close()
                
        except:
            print("insert domain extension error %s " % (cursor._last_executed)) 
        
        self.connection.commit()

    
    def selectDomainExtensionId(self, domainExtension):
        
        domainExtensionId = None

        try:
            with self.connection.cursor() as cursor:
                selectSQL = "SELECT id FROM domain_extension WHERE extension = %s"
                cursor.execute(selectSQL, (domainExtension.upper()))

                for row in cursor:
                    domainExtensionId = row['id']

                cursor.close()
        except Exception as e:
            print("select domain extension id error: %s " % (e))

        return domainExtensionId



    #######
    #   DOMAIN_RELATION
    ######
    def selectDomainRelationId(self, baseDomainId, relatedDomainId):
        selectSQL = "SELECT id FROM `domain_relation` WHERE base_domain_id = %s and related_domain_id = %s"
        domainRelationId = None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (baseDomainId, relatedDomainId))
                for row in cursor:
                    domainRelationId = row['id']
                cursor.close()
        except: 
            print("error selecting domain relation id")

        return domainRelationId

    def selectDomainRelationCount(self, domainRelationId):
        selectSQL = "SELECT count FROM domain_relation WHERE id = %s"
        count = 0
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (domainRelationId))
                for row in cursor:
                    count = row['count']
                cursor.close()
        except: 
            print("error selecting domain relation id")

        return count

    def selectRelatedFromBase(self, baseDomainId):
        selectSQL = "SELECT related_domain_id FROM domain_relation WHERE base_domain_id = %s"
        domainRelationId = None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (baseDomainId))
                for row in cursor:
                    domainRelationId = row['related_domain_id']
                cursor.close()
        except: 
            print("error selecting domain relation id")

        return domainRelationId

    def insertDomainRelation(self, baseDomainId, relatedDomainId):
        insertSQL = "INSERT INTO domain_relation (base_domain_id,related_domain_id) VALUES (%s, %s)"
        linkRelationId = None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insertSQL, (baseDomainId, relatedDomainId))
                linkRelationId = cursor.lastrowid
                cursor.close()
        except:
            print("error inserting domain relation %s " % (cursor._last_executed))

        self.connection.commit()

        return linkRelationId

    def updateLinkRelation(self, relationId, count=1):
        updateSQL = "UPDATE domain_relation SET count = count + %s WHERE id=%s"

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(updateSQL, (count, relationId))
                cursor.close()
        except:
            print("error updating link relation")

        self.connection.commit()

    def deleteDomainRelation(self, domainRelationId):
        deleteSQL = "DELETE FROM domain_relation WHERE id = %s"

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(deleteSQL, (domainRelationId))
                cursor.close()
        except:
            print("error deleting domain relation %s" % (cursor._last_executed))

        self.connection.commit()

    def insertOrUpdateLinkRelation(self, baseDomainId, relatedDomainId):
        domainRelationId = self.selectDomainRelationId(baseDomainId, relatedDomainId)

        if domainRelationId == None:
            # insert a new record
            domainRelationId = self.insertDomainRelation(baseDomainId, relatedDomainId)
        else:
            # update current record count
            self.updateLinkRelation(domainRelationId)

        return domainRelationId
        #print("domain:\t %s = %s \nextension:\t %s = %s",(baseDomain, relatedDomain, baseExtension, relatedExtension))
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insertSQL, (baseLink, relatedLink))
                cursor.close()
        except:
            print("error inserting link relation")

        """
    

    def updateLinkRelationBase(self, domain_relation_id, newDomainId):
        updateSQL = "UPDATE domain_relation SET base_domain_id = %s WHERE id = %s"

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(updateSQL, (domain_relation_id, id))
                cursor.close()
        except:
            print("error updating domain relation base id %s " % (cursor._last_executed))

        self.connection.commit()

 
    ## WEB SCRAPING
    def insertWord(self, word, wordCount=1):
        insertSQL = "INSERT INTO `word` (`word`,`word_count`) VALUES (%s, %s)"
        wordId = None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insertSQL, (word, wordCount))
                wordId = cursor.lastrowid
                cursor.close()
        except:
            print("error inserting word %s " % (cursor._last_executed))

        self.connection.commit()

        return wordId

    def updateWord(self, wordId, count):
        updateSQL = "UPDATE word SET word_count = word_count + %s WHERE id=%s"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(updateSQL, (count, wordId))
                cursor.close()
        except:
            print("error updating word %s " % (cursor._last_executed))

        self.connection.commit()

    def selectWord(self, word):
        selectSQL = "SELECT id FROM `word` WHERE word = %s"

        wordId = None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (word))
                for row in cursor:
                    wordId = row['id']
                cursor.close()
        except: 
            print("error selecting word %s " % (cursor._last_executed))

        return wordId

    def selectWordFromId(self, wordId):
        selectSQL = "SELECT word FROM `word` WHERE id = %s"

        word = None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (wordId))
                for row in cursor:
                    word = row['word']
                cursor.close()
        except: 
            print("error selecting word %s " % (cursor._last_executed))

        return word

    def selectWordsInRange(self, lower=0, top=100):
        selectSQL = "SELECT `word` FROM `word` ORDER BY `word_count` DESC"

        words = []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL)
                for row in cursor:
                    words.append(row['word'])

                cursor.close()
        except:
            print("error selecting words in range %s " % (cursor._last_executed))

        totalSize = len(words) 
        lowerLimit = int(totalSize*(lower/100))
        upperLimit = int(totalSize*(top/100))

        return words[lowerLimit:upperLimit]

    def selectWordIdsInRange(self, lower=0, top=100):
        selectSQL = "SELECT id FROM `word` ORDER BY `word_count` DESC"

        words = []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL)
                for row in cursor:
                    words.append(row['id'])

                cursor.close()
        except:
            print("error selecting words in range %s " % (cursor._last_executed))

        totalSize = len(words) 
        lowerLimit = int(totalSize*(lower/100))
        upperLimit = int(totalSize*(top/100))

        return words[lowerLimit:upperLimit]

    ######
    # Article
    #########

    def insertArticle(self, linkId):
        insertSQL = "INSERT INTO `article` (`link_id`) VALUES (%s)"
        articleId = None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insertSQL, (linkId))
                articleId = cursor.lastrowid
                cursor.close()
        except:
            print("error inserting article %s " % (cursor._last_executed))

        return articleId

    def insertArticleWord(self, articleId, wordId, count):
        insertSQL = "INSERT INTO `article_word` (`article_id`,`word_id`,`count`) VALUES (%s, %s, %s)"
        articleWordId = None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insertSQL, (articleId, wordId, count))
                articleWordId = cursor.lastrowid
                cursor.close()
        except:
            print("error inserting article word %s " % (cursor._last_executed))

        return articleWordId

    def selectArticleSize(self):
        selectSQL = "SELECT count(*) as count FROM article"
        count = 0
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL)
                for row in cursor:
                    count = row['count']
                cursor.close()
        except:
            print("error selecting article count %s " % (cursor._last_executed))

        return count

    def selectArticleFromWords(self, wordIds):
        selectSQL = "SELECT article_id FROM article_word WHERE word_id in (%s)"
        in_p=', '.join(list(map(lambda x: '%s', wordIds)))
        selectSQL = selectSQL % in_p
        articlesIds = []
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (wordIds))
                for row in cursor:
                    articlesIds.append(row['article_id'])
                cursor.close()
        except: 
            print("error selecting article from word ids: %s " % (cursor._last_executed))

        return articlesIds

    def selectWordsFromArticle(self, articleId):
        selectSQL = "SELECT word_id, count FROM article_word WHERE article_id = %s"

        wordIds = {}

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(selectSQL, (articleId))
                for row in cursor:
                    wordIds[row['word_id']] = row['count']
                cursor.close()
        except: 
            print("error selecting words form article id: %s " % (cursor._last_executed))

        return wordIds
   



