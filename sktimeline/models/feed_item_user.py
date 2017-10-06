from sktimeline import db
from datetime import datetime

class FeedItemUser(db.Model):
    __tablename__ = 'feed_item_users'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_identifier = db.Column(db.String(128))
    feed_type = db.Column(db.String(8) ) # github, twitter, slack
    feed_id = db.Column( db.BigInteger )
    user_data = db.Column( db.PickleType )
    # may want to add a datastamp here of last created/updated so can update the userdata when needed 

    __table_args__ = (db.Index('feed_user', "user_identifier", "feed_type", "feed_id"), )

    def __init__(self, user_identifier, feed_type, feed_id, user_data):
        self.user_identifier = user_identifier
        self.feed_type = feed_type
        self.feed_id = feed_id
        self.user_data = user_data

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

  