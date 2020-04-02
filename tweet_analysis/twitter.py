from decouple import config
import tweepy
import basilica
from .models import DB, Tweet, User

#Import Keys
TWITTER_AUTH = tweepy.OAuthHandler(
    config('TWITTER_CONSUMER_KEY'),
    config('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(
    config('TWITTER_ACCESS_TOKEN'),
    config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA = basilica.Connection(config('BASILICA_KEY'))


def add_user(username):

    user = TWITTER.get_user(username)
    db_user = User(id = user.id, name = user.screen_name)

    DB.session.add(db_user)

    current_timeline = user.timeline(
        count=250, exclude_replies = False, include_rts = False,
        tweet_mode = 'extended', since_id = db_user.newest_tweet_id)

    if current_timeline:
        db_user.newest_tweet_id = current_timeline[0].id

    for tweet in current_timeline:
        embedding = BASILICA.embed_sentence(tweet.full_text, model = 'twitter')
        db_tweet = Tweet(id = tweet.id, text = tweet.full_text[:300], embedding = embedding)
        db_user.tweets.append(db_tweet)
        DB.session.add(bd_tweet)

    DB.session.commit()


def add_followers():
    #while ratelimit not over threshhold
    pass

def add_user(user_id):
    pass


TWITTER_USERS = ['robert_zubrin', 'matt42kirby', 'elonmusk', 'TexasDSHS', 'TXMilitary']

def add_users(users=TWITTER_USERS):
    """
    Add/update a list of users (strings of user names).
    May take awhile, so run "offline" (flask shell).
    """
    for user in users:
        add_user(user)
