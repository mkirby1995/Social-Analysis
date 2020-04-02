from decouple import config
import tweepy
import basilica
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from .models import DB, User, Tweet
from .twitter import add_user, add_users


"""
Search twitter for topic
Spin up and run every x hours
Find out how many new tweets user has
See who retweeted a tweet
Run topic analysis on their timeline
Sentiment analysis on tweets ?? any good ??
Tweets per day?
"""

#Import Keys
TWITTER_AUTH = tweepy.OAuthHandler(
    config('TWITTER_CONSUMER_KEY'),
    config('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(
    config('TWITTER_ACCESS_TOKEN'),
    config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA = basilica.Connection(config('BASILICA_KEY'))


def create_app():
    """Create and configure an instance of the flask application"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)


    @app.route('/')
    def root():
        users = User.query.all()
        return render_template("index.html")


    # Get topics last 250 tweets
    @app.route('/topics')
    def user_topic():
        # Create user
        user = TWITTER.get_user('matt42kirby')
        # Create corpus
        timeline = new_corpus(user.timeline(
            count=250,
            exclude_replies = False,
            include_rts = False,
            tweet_mode = 'extended')
            )
        # Get topics
        topics = mallet_topics(timeline)

        return jsonify(topics)


    # Get text of users last 250 tweets
    @app.route('/timeline/<username>', methods = ['GET'])
    def timeline(username):
        # Create user
        user = TWITTER.get_user(username)
        timeline = user.timeline(
            count=250,
            exclude_replies = False,
            include_rts = False,
            tweet_mode = 'extended')
        timeline = [tweet.full_text for tweet in timeline]
        return jsonify(timeline)


    return app
