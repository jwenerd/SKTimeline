# -*- coding: utf-8 -*-
from sktimeline import db, nlp
from HTMLParser import HTMLParser
from collections import Counter
import re

from sktimeline.models.twitter import TwitterFeedSetting, TwitterFeedItem
from sktimeline.models.slack import SlackFeedItemFormatter, SlackFeedSetting
from sktimeline.models.github import GithubFeedSetting


class UserFeedsTokenizer:

    def __init__(self, user_id):
        self.user_id = user_id
        self.__init_twitter()
        self.__init_slack()
        self.__init_github()
    
    def most_common_words(self, count = 200): 
        # five most common tokens
        words = self.slack_tokenizer.words + self.twitter_tokenizer.words + self.github_tokenizer.words
        word_freq = Counter(words)
        common_words = word_freq.most_common(count)
        return common_words

    def __init_twitter(self):
        twitter_settings_ids = list( map( lambda feed: feed.id, TwitterFeedSetting.belonging_to_user( self.user_id ) ) )
        twitter_feed_items = TwitterFeedItem.query.filter(TwitterFeedItem.twitter_feed_id.in_(twitter_settings_ids)).all()
        tweets = list( map( lambda tweet: tweet.tweet_data.text, twitter_feed_items) )
        self.twitter_tokenizer = TwitterItemsTokenizer(tweets)

    def __init_slack(self):
        slack_feeds = SlackFeedSetting.belonging_to_user( self.user_id )
        slack_items = []
        for feed in slack_feeds:
            messages = [ item for item in feed.feed_items if (item.data['type'] == 'message' and 'subtype' not in item.data)]
            items = list( map( lambda item: SlackFeedItemFormatter(feed,item).message_text, messages) )
            slack_items.append(items)

        slack_items = [item for sublist in slack_items for item in sublist]
        self.slack_tokenizer = SlackItemsTokenizer(slack_items)
    
    def __init_github(self):
        github_feeds = GithubFeedSetting.belonging_to_user( self.user_id )
        github_items = []
        for feed in github_feeds:
            items = list( map( lambda item: item.git_commit_data['message'], feed.feed_items) )
            github_items.append(items)

        github_items = [item for sublist in github_items for item in sublist]
        self.github_tokenizer = GithubItemsTokenizer(github_items)

class FeedItemTokenizer(object):

    # may be possible to add custom tokenization rule for this 
    html_parser = HTMLParser()
    def __init__(self):
        self._words = False
        self._set = False

    @property
    # all the token text with repeated values to count frequency 
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

class TwitterItemsTokenizer(FeedItemTokenizer):
    
    def __init__(self, tweets):
        super(TwitterItemsTokenizer, self).__init__()
        self.tweets = list( map( lambda text: self.__class__.replace_entities(text) , tweets) )
        text = "\n".join(self.tweets) 
        self.doc = nlp.tokenizer(text)
    
    @classmethod
    def replace_entities(cls, text):
        return cls.html_parser.unescape(text)


class SlackItemsTokenizer(FeedItemTokenizer):
    
    def __init__(self, messages):
        super(SlackItemsTokenizer, self).__init__()
        self.messages = list( map( lambda text: self.__class__.clean_text(text), messages) )
        text = "\n".join(self.messages) 
        self.doc = nlp.tokenizer(text)

    @classmethod
    def clean_text(cls, text):
        # text like `look at this:<a href=... ` - add a space so url broken out and doesn't run in to prev word
        text = text.replace('<a href=',' <a href=')
        # now strip away all the tags and just use the message text 
        text = re.sub('<[^<]+?>','',text)
        text = cls.html_parser.unescape(text) 
        return text


class GithubItemsTokenizer(FeedItemTokenizer):
    
    def __init__(self, commits):
        super(GithubItemsTokenizer, self).__init__()
        self.commits = list( map( lambda text: self.__class__.replace_entities(text) , commits) )
        text = "\n".join(self.commits) 
        self.doc = nlp.tokenizer(text)

    @classmethod
    def replace_entities(cls, text):
        return text
        # return cls.html_parser.unescape(text)