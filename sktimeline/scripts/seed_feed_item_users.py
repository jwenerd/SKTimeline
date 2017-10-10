from sktimeline.models import *
from sktimeline import db

# This is a utility class to feed the seed data
#  when migrating from the previous version 
#  to new schema where the user info per-feed is stored in the feed_item_users table

class SeedFeedItemUsers():

    UPDATE_QUERY_LIMIT = 1000

    @classmethod
    def twitter(cls):
        count = TwitterFeedItem.query.filter_by(feed_user_id=None).count()
        while count > 0:
            print "updates left: " + str(count) + "\n"
            items = TwitterFeedItem.query.filter_by(feed_user_id=None).limit(cls.UPDATE_QUERY_LIMIT).all()
            for item in items:
                item.store_feed_user()
            db.session.commit()
            count = TwitterFeedItem.query.filter_by(feed_user_id=None).count()
        return None

    @classmethod
    def github(cls):
        count = GithubFeedItem.query.filter_by(feed_user_id=None).count()
        while count > 0:
            print "updates left: " + str(count) + "\n"
            items = GithubFeedItem.query.filter_by(feed_user_id=None).limit(cls.UPDATE_QUERY_LIMIT).all()
            for item in items:
                item.store_feed_user()
            db.session.commit()
            count = GithubFeedItem.query.filter_by(feed_user_id=None).count()
        
        return None

    @classmethod
    def slack(cls):
        count = SlackFeedItem.query.filter_by(feed_user_id=None).count()
        while count > 0:
            print "updates left: " + str(count) + "\n"
            items = SlackFeedItem.query.filter_by(feed_user_id=None).limit(cls.UPDATE_QUERY_LIMIT).all()
            for item in items:
                item.store_feed_user()
            db.session.commit()
            count = SlackFeedItem.query.filter_by(feed_user_id=None).count()
            
        return None