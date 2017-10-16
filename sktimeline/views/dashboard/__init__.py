from sktimeline import *
from sktimeline.views import login_required, page_not_found
from wtforms import validators
import json

import twitter
import github
import slack


#Dashboard
@app.route('/dashboard/')
@login_required
def dashboard():
    twitter_settings = TwitterFeedSetting.belonging_to_user(session['user_id'])
    slack_settings = SlackFeedSetting.belonging_to_user(session['user_id'])
    github_settings = GithubFeedSetting.belonging_to_user(session['user_id'])
    #TODO: maybe user object and ORM methods - depends on where other settings going
    return render_template("dashboard.html", twitter_settings = twitter_settings,
                                             slack_settings = slack_settings,
                                             github_settings = github_settings)


#Dashboard
@app.route('/dashboard/text')
@login_required
def dashboard_text():
    twitter_settings_ids = list( map( lambda feed: feed.id, TwitterFeedSetting.belonging_to_user(session['user_id']) ) )
    twitter_feed_items = TwitterFeedItem.query.filter(TwitterFeedItem.twitter_feed_id.in_(twitter_settings_ids)).all()
    tweets = list( map( lambda tweet: tweet.tweet_data.text, twitter_feed_items) )
    tokens = TwitterItemsTokenizer(tweets)
    word_counts = tokens.most_common_words(200)

    return render_template("dashboard/text.html", tokens = tokens, word_counts = word_counts)



@app.route('/dashboard/timeline')
@login_required
def dashboard_timeline():
    current_user = User.query.get( session['user_id'] )
    feed_groups = []
    feed_groups_data = {};
    # these are very repetitive... find way to dry
    for twitter_feed_setting in current_user.twitter_feed_settings:
        unique_id = 'twitter-'+str(twitter_feed_setting.id)
        feed_groups_data[unique_id] = []
        for item in twitter_feed_setting.feed_items:
            formatter = TwitterFeedItemFormatter( twitter_feed_setting, item )
            feed_groups_data[unique_id].append( formatter.to_json )
        if len(feed_groups_data[unique_id]):
            feed_groups.append( {'id': unique_id, 'text': feed_groups_data[unique_id][0]['group']})
        else:
            feed_groups_data.pop(unique_id, None)

    for github_feed_setting in current_user.github_feed_settings:
        unique_id = 'github-'+str(github_feed_setting.id)
        feed_groups_data[unique_id] = []
        for item in github_feed_setting.feed_items:
            formatter = GithubFeedItemFormatter(github_feed_setting, item )
            feed_groups_data[unique_id].append( formatter.to_json )
        if len(feed_groups_data[unique_id]):
            feed_groups.append({'id': unique_id, 'text': feed_groups_data[unique_id][0]['group'] })
        else:
            feed_groups_data.pop(unique_id, None)


    for slack_feed_setting in current_user.slack_feed_settings:
        unique_id = 'slack-'+str(slack_feed_setting.id)
        feed_groups_data[unique_id] = []
        for item in slack_feed_setting.feed_items:
            formatter = SlackFeedItemFormatter(slack_feed_setting,item)
            feed_groups_data[unique_id].append( formatter.to_json )

        if len(feed_groups_data[unique_id]):
            feed_groups.append( {'id': unique_id, 'text': feed_groups_data[unique_id][0]['group'] })
        else:
            feed_groups_data.pop(unique_id, None)

    return render_template('dashboard/timeline.html', feed_groups_data=json.dumps(feed_groups_data),
                                                      feed_groups=json.dumps(feed_groups) )
