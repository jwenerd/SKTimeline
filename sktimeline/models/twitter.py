# -*- coding: utf-8 -*-
from sktimeline import db
from sktimeline import tweepy, tweepy_API, nlp
from sktimeline.models.feed_item_user import FeedItemUser
from datetime import datetime
import re

class TwitterFeedSetting(db.Model):
    __tablename__ = 'feed_setting_twitter'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    # handle = db.Column( db.String(64) )
    hashtag = db.Column( db.String(128), default=None)
    status = db.Column( db.String(64), default=None)
    last_updated = db.Column( db.DateTime(timezone=True), default=None )

    feed_items = db.relationship( 'TwitterFeedItem' , backref='feed_setting_twitter', cascade="all, delete-orphan", lazy='select')

    #todo: move method that starts adding hashtags here

    def set_updating(self):
        self.status = 'updating'
        db.session.commit()
        return self

    def set_updated(self):
        self.status = 'updated'
        self.last_updated = datetime.now()
        db.session.commit()
        return self

    def start_populate(self):
        # download 200 latest tweets with this hash tag, this can go up to 1500 according to twitter api docs
        self.download_tweets(max_tweets=200)
        return True

    def get_last_tweet_id_downloaded(self):
        return db.session.query(db.func.max( TwitterFeedItem.tweet_id) ).filter_by(twitter_feed_id=self.id).scalar()

    def download_tweets(self, since_id=False, max_tweets=100):

        query = self.hashtag
        self.set_updating()
        if since_id:
            hashtag_tweets = [status for status in tweepy.Cursor(tweepy_API.search, rpp=100, q=query, since_id=since_id).items(max_tweets)]
        else:
            hashtag_tweets = [status for status in tweepy.Cursor(tweepy_API.search, rpp=100, q=query).items(max_tweets)]

        for tweet in hashtag_tweets:
            feed_item = TwitterFeedItem(tweet.id, self.id, tweet)
            feed_item.store_feed_user() # tbd: should go in constructor?
            db.session.add(feed_item)
        self.set_updated()
        db.session.commit()


    def do_feed_update(self):
        last_tweet = self.get_last_tweet_id_downloaded()
        if ( not(last_tweet) ):
            self.start_populate()
        else:
            self.download_tweets(since_id=last_tweet)
        return True

    @classmethod
    def belonging_to_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def update_items(cls):
        items = cls.query.filter_by(status='updated').all()
        for item in items:
            item.do_feed_update()
        db.session.close()
        return True


    @classmethod
    def new_items(cls):
        return cls.query.filter_by(status='new').all()

    @classmethod
    def start_populate_new_items(cls):
        new_items = cls.new_items()
        for item in new_items:
            item.start_populate()
        db.session.close()
        return True





class TwitterFeedItem(db.Model):
    __tablename__ = 'twitter_feed_items'
    id = db.Column(db.BigInteger, primary_key=True)
    twitter_feed_id = db.Column(db.Integer, db.ForeignKey('feed_setting_twitter.id'))
    tweet_id = db.Column( db.BigInteger )
    tweet_retrieved = db.Column( db.DateTime(timezone=True), default=datetime.now )
    tweet_data = db.Column( db.PickleType )
    feed_user_id = db.Column( db.BigInteger, db.ForeignKey('feed_item_users.id') )

    def __init__(self, tweet_id, twitter_feed_id, tweet_data):
        self.tweet_id = tweet_id
        self.twitter_feed_id = twitter_feed_id
        self.tweet_data = tweet_data

    def store_feed_user(self):
        if self.feed_user_id == None:
            twitter_user_id = self.tweet_data.user.id
            # tbd:  self.tweet_data.user is way to large making table size huge, 
            # - let's just store like a dict of username and profile 
            feed_user = FeedItemUser.get_or_create( twitter_user_id, 'twitter', self.twitter_feed_id, self.tweet_data.user)
            self.feed_user_id = feed_user.id


    @property
    def status_url(self):
        return ( 'https://twitter.com/statuses/' + str(self.tweet_id) )



class TwitterFeedItemFormatter:
    def __init__(self, twitter_feed_setting, feed_item):
        self.twitter_feed_setting = twitter_feed_setting
        self.feed_item = feed_item
        self.timestamp = self.feed_item.tweet_data.created_at
        self._photo_media_url = None

    def photo_media_url(self):
        if self._photo_media_url is not None:
            return self._photo_media_url

        self._photo_media_url = False
        if not 'media' in self.feed_item.tweet_data.entities:
            return False

        for e in self.feed_item.tweet_data.entities['media']:
            if 'type' in e and e['type'] == 'photo':
                self._photo_media_url = e['media_url']
                break
        return self._photo_media_url


    @property
    def unique_id(self):
        hashtag_attr = self.twitter_feed_setting.hashtag.strip()
        #hashtag as attribute - remove spaces and non alpha numeric chars
        hashtag_attr = re.sub(r"[^\w\s]", '', hashtag_attr)
        # Replace all runs of whitespace with a single dash
        hashtag_attr = re.sub(r"\s+", '-', hashtag_attr)

        return 'tweet-' + hashtag_attr + '-' + str(self.feed_item.tweet_id)

    @property
    def to_json(self):
        obj = {}
        obj['type'] = 'twitter'
        obj['tweet_text'] = self.feed_item.tweet_data.text
        obj['group'] = 'Twitter: ' + self.twitter_feed_setting.hashtag
        obj['unique_id'] = self.unique_id
        obj['media'] = {
            'url': self.feed_item.status_url
            # todo: add thumbnail here
        }
        media_url = self.photo_media_url()
        if media_url:
            obj['background'] = { 'url': media_url }
        obj['start_date'] = {
          'year': self.timestamp.year,
          'month': self.timestamp.month,
          'day': self.timestamp.day,
          'hour': self.timestamp.hour,
          'minute':  self.timestamp.minute,
          'second':  self.timestamp.second
        }
        return obj


from HTMLParser import HTMLParser
from collections import Counter

class TwitterItemsTokenizer:
    
    # may be possible to add custom tokenization rule for this 
    html_parser = HTMLParser()
    

    def __init__(self, tweets):
        self.tweets = list( map( lambda text: self.__class__.replace_entities(text) , tweets) )
        text = "\n".join(self.tweets) 
        self.doc = nlp.tokenizer(text)
        self._words = False
        self._set = False

    @classmethod
    def replace_entities(cls, text):
        return cls.html_parser.unescape(text)

    IGNORE_LIST = ['RT',"n't",u'n’t', 'w/'] 

    @classmethod
    def include_token(cls, token):
        if token.is_punct or token.is_space or token.like_url or token.is_digit or token.is_stop:
            return False
        elif token.text in cls.IGNORE_LIST:
            return False
        elif len(token.text) == 1:
            # remove single chars
            return False
        elif re.match('^(.*@)',token.text):
            # do not include twitter handles starting with like @handle
            #  or dot style handle replys starting with .@handle or any chars like -@handle
            #  may instead want to include twitter handles regularized as @handle for wordcount and seeing who in discussion
            return False 
        elif re.match('^(\W.*)',token.text):
            #  remove anything that starts with a non-word char
            #  removing things like the contraction suffixes "'re"  "'ve"  and emojis chars 
            #  consequencely things like /overcome, /whose/ where words extracted from strings with /
            #    like " where/when/whenever ", etc

            return False
        elif re.match('^(http.*)',token.text):
            # some tokens relu 
            return False
        
        return True

    def most_common_words(self, count): 
        # five most common tokens
        word_freq = Counter(self.words)
        common_words = word_freq.most_common(count)
        return common_words

    @property
    def words(self):
        if self._words == False:
            self._words = [token.text for token in self.doc if self.__class__.include_token(token)]
            self._words.sort()
        return self._words

    @property
    # unique elements without frequency of the tokens
    def set(self):
        if self._set == False:
            self._set = list(set(self.words))
            self._set.sort()
        return self._set
    