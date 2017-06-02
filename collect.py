import tweepy
import json
from tweepy import OAuthHandler
from tweepy import StreamListener
from mysqldb import Mysqldb
import pymysql
from config import *
from linkUtils import LinkUtils

# Variables that contains the user credentials to access Twitter API
consumer_key = 'O9x02NEsZyaOZ9x4vUmLrw3Ds'
consumer_secret = '8eJnaPf6ishuFNBPNGZAqK0ecODiTs60VnLcsaGN5CBqhABmEG'
access_token = '3004912756-JlfYMfxVdChpsdZhOd0S7f1HoshbCElqwaZjpMk'
access_token_secret = 'Toe58VSOuLAMd4WrDRdLzspwoTCe71xvl8ZEcsgb3iZcV'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)



"""
public_tweets = api.home_timeline()
for tweet in public_tweets:
    print (tweet.text)
"""
"""
class MyStreamListener(tweepy.StreamListener):

    def on_error(self, status_code):
    	print (status)
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)

myStream.filter(track=['this','and','you','now','year','start','or','if',' ', 'the'], async=True)
"""
class MyStreamListener(tweepy.StreamListener):
    def __init__(self, db, api=None):
        super(MyStreamListener, self).__init__(api)
        self.linkUtils = LinkUtils()
        self.db = db

    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        tweet = json.loads(data)
        
        if tweet != None and "lang" in tweet and tweet['lang'] == "en" and 'entities' in tweet and 'urls' in tweet['entities']:
            urls = tweet['entities']['urls']
            links = []

            for url in urls:
                if url['expanded_url'] != None:
                    links = links + [self.db.insertLink(url['expanded_url'])]
            if len(links) > 0 and not all(link is None for link in links):
                userId = self.db.insertUser(tweet)
                self.db.insertTweet(userId, tweet, links)   
    
        return True

    def on_error(self, status):
        print (self)
        print (status)


if __name__ == '__main__':
    with Mysqldb(**mysqlconfig) as db:
        myStreamListener = MyStreamListener(db)
        myStream = tweepy.Stream(auth=auth, listener=myStreamListener)
        myStream.filter(track=['flu','cancer','influenca','disease','treatment'])

    
    print ("Showing all new tweets for the selected tags:")

    # There are different kinds of streams: public stream, user stream, multi-user streams
    # In this example follow #programming tag
    # For more details refer to https://dev.twitter.com/docs/streaming-apis
    # stream = tweepy.Stream(auth, l)
    


