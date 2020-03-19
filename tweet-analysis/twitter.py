from decouple import config
import tweepy
import basilica

#Import Keys
TWITTER_AUTH = tweepy.OAuthHandler(
    config('TWITTER_CONSUMER_KEY'),
    config('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(
    config('TWITTER_ACCESS_TOKEN'),
    config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA = basilica.Connection(config('BASILICA_KEY'))



# Get user timeline tweets
def get_timeline(username):
    user = TWITTER.get_user(username)
    timeline = user.timeline(
        count=250,
        exclude_replies = False,
        include_rts = False,
        tweet_mode = 'extended')
    timeline = [tweet.full_text for tweet in timeline]
    return timeline
