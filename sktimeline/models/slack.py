from sktimeline import db
from datetime import datetime
from slackclient import SlackClient


class SlackFeedSetting(db.Model):
    __tablename__ = 'feed_setting_slack'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    status = db.Column( db.String(64), default=None)
    last_updated = db.Column( db.DateTime(timezone=True), default=None )

    # holds the token info, user id, team id, team name
    slack_auth_info = db.Column( db.PickleType )

    # slack machine readable id used for api request
    channel_id = db.Column( db.String(128), default=None)
    # channel info like name/description, members, etc
    channel_info = db.Column( db.PickleType )

    feed_items = db.relationship( 'SlackFeedItem' , backref='slack_feed_items', cascade="all, delete-orphan", lazy='select')


    _slack_client = False

    def __init__(self):
        self.status = 'new'
        self.last_updated = datetime.now()

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
        self.download_history(count=100)
        return True

    def download_history(self,count=100, oldest=0):
        self.set_updating()
        response = self.slack_client.api_call('channels.history', channel=self.channel_id, count=count, oldest=oldest)
        if response['messages']:
            for message in response['messages']:
                feed_item = SlackFeedItem()
                feed_item.timestamp = datetime.utcfromtimestamp( float(message['ts']) )
                feed_item.slack_feed_id = self.id
                feed_item.data = message
                db.session.add(feed_item)

        self.set_updated()
        db.session.commit()
        return response

    @property
    def latest_feed_item(self):
        items = SlackFeedItem.query.order_by(
                            db.desc( SlackFeedItem.timestamp  )
                        ).filter_by(
                            slack_feed_id=self.id
                        ).limit(1).all()

        if len(items) == 1:
            return items[0]
        else:
            return False

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

    def do_update(self):
        oldest = 0
        if self.latest_feed_item:
            oldest = self.latest_feed_item.ts
        self.download_history(count=1000, oldest=oldest)
        # todo: will need to see how to handle this if there are > 1000 messages to add
        return True

    @classmethod
    def update_items(cls):
        items = cls.query.filter_by(status='updated').all()
        for item in items:
            item.do_update()
        db.session.close()
        return True

    @property
    def slack_client(self):
        if not self.is_token_info_present :
            return False
        if not self._slack_client:
            self._slack_client = SlackClient(self.token)
        return self._slack_client


    @property
    def team_name(self):
        if not self.slack_auth_info:
            return False
        return self.slack_auth_info['team_name']

    @property
    def is_channel_info_present(self):
        if not self.channel_info:
            return False
        return True

    @property
    def channel_name(self):
        if not self.is_channel_info_present:
            return False
        return self.channel_info['name']

    @property
    def is_token_info_present(self):
        if not self.slack_auth_info:
            return False
        if not self.slack_auth_info['access_token']:
            return False
        return True

    @property
    def token(self):
        if not self.is_token_info_present:
            return False
        return self.slack_auth_info['access_token']


    @classmethod
    # todo: these can be dry by using module I think
    def belonging_to_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()



class SlackFeedItem(db.Model):
    __tablename__ = 'slack_feed_items'
    id = db.Column(db.BigInteger, primary_key=True)
    slack_feed_id = db.Column(db.Integer, db.ForeignKey('feed_setting_slack.id'))
    timestamp = db.Column( db.DateTime(timezone=True), default=None )
    data = db.Column( db.PickleType )

    @property
    def ts(self):
        return self.data['ts']

    @property
    def to_json(self):
        obj = {}
        obj['data'] = self.data
        obj['text'] = {
            'text': self.data['text']
        }
        obj['start_date'] = {
          'year': self.timestamp.year,
          'month': self.timestamp.month,
          'day': self.timestamp.day,
          'hour': self.timestamp.hour,
          'minute':  self.timestamp.minute,
          'second':  self.timestamp.second
        }

        return obj
