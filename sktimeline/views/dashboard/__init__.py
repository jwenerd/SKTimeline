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




@app.route('/dashboard/timeline')
@login_required
def dashboard_timeline():
    current_user = User.query.get( session['user_id'] )

    twitter_feed_items = []
    for twitter_feed_setting in current_user.twitter_feed_settings:
        for item in twitter_feed_setting.feed_items:
            formatter = TwitterFeedItemFormatter( twitter_feed_setting, item )
            twitter_feed_items.append( formatter.to_json )

    github_feed_items = []
    for github_feed_setting in current_user.github_feed_settings:
        for item in github_feed_setting.feed_items:
            formatter = GithubFeedItemFormatter(github_feed_setting, item )
            github_feed_items.append( formatter.to_json )

    slack_feed_items = []
    for slack_feed_setting in current_user.slack_feed_settings:
        for item in slack_feed_setting.feed_items:
            formatter = SlackFeedItemFormatter(slack_feed_setting,item)
            slack_feed_items.append( formatter.to_json )

    return render_template('dashboard/timeline.html', twitter_feed_items=json.dumps(twitter_feed_items),
                                                      github_feed_items=json.dumps(github_feed_items),
                                                      slack_feed_items=json.dumps(slack_feed_items) )
