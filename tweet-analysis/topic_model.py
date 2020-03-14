# Generate a topic model given a username
from decouple import config

import tweepy
import basilica
import nltk
import numpy as np
import pandas as pd
from pprint import pprint
import re

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

# spacy for lemmatization
import spacy

# NLTK Stop words
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'https', 'try', 'http'])

nlp = spacy.load('en_core_web_lg', disable=['parser', 'ner'])
mallet_path = '/Users/mattkirby/Social-Analysis/tweet-analysis/mallet-2.0.8/bin/mallet' # update this path


TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),
                                   config('TWITTER_CONSUMER_SECRET'))

TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                              config('TWITTER_ACCESS_TOKEN_SECRET'))

TWITTER = tweepy.API(TWITTER_AUTH)

BASILICA = basilica.Connection(config('BASILICA_KEY'))


def get_tweets(username):
        # Retrive tweets
        twitter_user = TWITTER.get_user('matt42kirby')
        tweets = twitter_user.timeline(
                count=250, exclude_replies = False, include_rts = False,
                tweet_mode = 'extended')
        return tweets


def topic_model(corpus):

    # Clean corpus
    def tokenize(corpus):
        for tweet in corpus:
            yield(gensim.utils.simple_preprocess(
                str(tweet.full_text), deacc=True))

    data_words = list(tokenize(corpus))

    # Build the bigram and trigram models
    bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100) # higher threshold fewer phrases.
    trigram = gensim.models.Phrases(bigram[data_words], threshold=100)

    # Faster way to get a sentence clubbed as a trigram/bigram
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)


    # Define functions for stopwords, bigrams, trigrams and lemmatization
    def remove_stopwords(texts):
        return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

    def make_bigrams(texts):
        return [bigram_mod[doc] for doc in texts]

    def make_trigrams(texts):
        return [trigram_mod[bigram_mod[doc]] for doc in texts]

    def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        """https://spacy.io/api/annotation"""
        texts_out = []
        for sent in texts:
            doc = nlp(" ".join(sent))
            texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
        return texts_out


    # Remove Stop Words
    data_words_nostops = remove_stopwords(data_words)

    # Form Bigrams
    data_words_bigrams = make_bigrams(data_words_nostops)

    # Do lemmatization keeping only noun, adj, vb, adv
    data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

    # Create Dictionary
    id2word = corpora.Dictionary(data_lemmatized)

    # Create Corpus
    texts = data_lemmatized


    # Term Document Frequency
    corpus = [id2word.doc2bow(text) for text in texts]

    ldamallet = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=20, id2word=id2word)

    topics = {}

    for i in range(0, ldamallet.num_topics):
        topic = []
        for word_record in ldamallet.print_topic(i).split('+'):
            topic.append((word_record.split("*")[0], word_record.split("*")[1].replace('"', "").replace(' ', "")))
        topics['topic' + str(i)] = topic

    return topics
