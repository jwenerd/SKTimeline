from sktimeline import db
from datetime import datetime


class FeedItemUser(db.Model):
    __tablename__ = 'feed_item_users'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_identifier = db.Column(db.String(128))
    feed_type = db.Column(db.String(8) ) # github, twitter, slack  - tbd: conver tthis to a enum for < storage 
    feed_id = db.Column( db.BigInteger )
    user_data = db.Column( db.PickleType )
    _feed_items = False
    # todo: may want to add a datastamp here of last created/updated so can update the userdata when needed 
    # todo: may want to store display_name column with twitter @handle, slack display name, github email or name field?
 

    __table_args__ = (db.Index('feed_user', "user_identifier", "feed_type", "feed_id"), db.Index('feed_id', "feed_id"), )

    def __init__(self, user_identifier, feed_type, feed_id, user_data):
        self.user_identifier = user_identifier
        self.feed_type = feed_type
        self.feed_id = feed_id
        self.user_data = user_data
        self._feed_items = False

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


    
  