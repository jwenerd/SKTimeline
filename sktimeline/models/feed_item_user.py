from sktimeline import db
from datetime import datetime
from sktimeline.models.slack import SlackFeedSetting

class FeedItemUser(db.Model):
    __tablename__ = 'feed_item_users'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_identifier = db.Column(db.String(128)) # for slack and github data
    twitter_id = db.Column( db.BigInteger )
    feed_type = db.Column( db.Enum('github','twitter','slack', name="feed_type_enum") ) # github, twitter, slack  - tbd: conver tthis to a enum for < storage 
    display_name = db.Column(db.String(256))
    _feed_items = False
    # todo: may want to add a datastamp here of last created/updated so can update the userdata when needed 
    
    __table_args__ = ( db.Index('twitter_id', "twitter_id"), db.Index('feed_type', "feed_type"),  db.Index('user_identifier', "user_identifier") )

    def __init__(self):
        pass

    @property
    def feed_items(self):
        if self._feed_items != False:
            return self._feed_items
        elif self.feed_type == 'twitter':
            from sktimeline.models.twitter import TwitterFeedItem  # :/ not sure the proper way to handle this yet
            cls = TwitterFeedItem
        elif self.feed_type == 'github':
            from sktimeline.models.github import GithubFeedItem
            cls = GithubFeedItem
        elif self.feed_type == 'slack':
            from sktimeline.models.slack import SlackFeedItem
            cls = SlackFeedItem
        
        print 'querying feed items -- '
        self._feed_items = cls.query.filter_by(feed_user_id=self.id).all()
        return self._feed_items

    @classmethod
    def get_or_create(cls, user_identifier, feed_type, feed_id, user_data):
        instance = cls.query.filter_by(user_identifier=user_identifier, feed_type=feed_type, feed_id=feed_id).first()
        if instance:
            return instance
        else:
            instance = cls(user_identifier, feed_type, feed_id, user_data)
            db.session.add(instance)
            db.session.commit()
            return instance


class TwitterFeedItemUser(FeedItemUser):

    def __init__(self, twitter_id, display_name):
        self.twitter_id = twitter_id
        self.feed_type = 'twitter'
        self.display_name = display_name

    @classmethod
    def get_or_create(cls, twitter_id, user_data):
        instance = cls.query.filter_by(twitter_id=twitter_id, feed_type='twitter').first()
        if instance:
            return instance
        else:
            instance = cls(twitter_id, user_data.screen_name)
            db.session.add(instance)
            db.session.commit()
            return instance

class GithubFeedItemUser(FeedItemUser):
    def __init__(self, user_identifier, display_name):
        self.feed_type = 'github'
        self.user_identifier = user_identifier # the git commit email
        self.display_name = display_name # the git commit name string

    @classmethod
    def get_or_create(cls, committer):
        user_identifier = committer['email']
        display_name = committer['name']
        instance = cls.query.filter_by(user_identifier=user_identifier, feed_type='github').first()
        if instance:
            return instance
        else:
            instance = cls(user_identifier, display_name)
            db.session.add(instance)
            db.session.commit()
            return instance


class SlackFeedItemUser(FeedItemUser):
    def __init__(self, user_identifier, display_name):
        self.feed_type = 'slack'
        self.user_identifier = user_identifier # the git commit email
        self.display_name = display_name # the git commit name string

    @classmethod
    def get_or_create(cls, slack_user_id, slack_feed_id):
            user_identifier = str(slack_feed_id) + ':' + slack_user_id 
            instance = cls.query.filter_by(user_identifier=user_identifier, feed_type='slack').first()
            if instance:
                return instance
            else:
                slack_feed = SlackFeedSetting.query.get(slack_feed_id)
                display_name = ''
                user_info = slack_feed.slack_user_info(slack_user_id)
                if user_info:
                    display_name = user_info.get('real_name','')
                
                instance = cls(user_identifier, display_name)
                db.session.add(instance)
                db.session.commit()
                return instance