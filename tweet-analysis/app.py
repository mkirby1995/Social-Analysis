from decouple import config
from flask import Flask, render_template, request, jsonify
from .topic_model import topic_model, get_tweets
import os

TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),
                                   config('TWITTER_CONSUMER_SECRET'))

TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                              config('TWITTER_ACCESS_TOKEN_SECRET'))

TWITTER = tweepy.API(TWITTER_AUTH)

BASILICA = basilica.Connection(config('BASILICA_KEY'))

def create_app():
    app = Flask(__name__)
    #app.config["SQLAlchemy_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    #app.config["ENV"] = config("ENV")
    #DB.init-app(app)

    @app.route('/')
    def root():
        return 'Success!'

    # Get Followers

    # Get topics of current feed
    @app.route('/feed_topics')
    def feed_topic():
        topics = topic_model(TWITTER.home_timeline())
        return jsonify(topics)

    return app
