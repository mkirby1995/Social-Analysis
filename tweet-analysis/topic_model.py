# Generate a topic model given a username
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

# Plotting tools
import pyLDAvis
import pyLDAvis.gensim  # don't skip this
import matplotlib.pyplot as plt
%matplotlib inline

# NLTK Stop words
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'https', 'try', 'http'])

spacy.load('en')

mallet_path = '/content/mallet-2.0.8/bin/mallet' # update this path


TWITTER_AUTH = tweepy.OAuthHandler('KSRGR9mHi8uksXocrmftDwGpj',
                                   'KH2CCKo1uEnuPyv7jys50IOu0gtw2hMCEcvRWO0100IwhVKnJ2')

TWITTER_AUTH.set_access_token('219574192-Dw9dsBrkLwa36OCF1yoLdGalT4nD2w0ByGHKB762',
                              'eMUXUCS7JcIUCqaF7FofH9zVjNiWZMpuexNRzOX4OgMgP')

TWITTER = tweepy.API(TWITTER_AUTH)

#TODO: Remove key with decouple
BASILICA = basilica.Connection('94bdb651-fa65-4a60-9db2-a64335b8bc74')


def topic_model():


    # Retrive tweets
    twitter_user = TWITTER.get_user('matt42kirby')
    tweets = twitter_user.timeline(
            count=250, exclude_replies = False, include_rts = False,
            tweet_mode = 'extended')


    # Clean corpus
    def tokenize(tweets):
        for tweet in tweets:
            yield(gensim.utils.simple_preprocess(
                str(tweet.full_text), deacc=True))

    data_words = list(tokenize(tweets))

    # Build the bigram and trigram models
    #bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100) # higher threshold fewer phrases.
    #trigram = gensim.models.Phrases(bigram[data_words], threshold=100)

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

    # python3 -m spacy download en
    nlp = spacy.load('en', disable=['parser', 'ner'])

    # Do lemmatization keeping only noun, adj, vb, adv
    data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

    # Create Dictionary
    id2word = corpora.Dictionary(data_lemmatized)

    # Create Corpus
    texts = data_lemmatized


    # Term Document Frequency
    corpus = [id2word.doc2bow(text) for text in texts]

    ldamallet = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=20, id2word=id2word)

    return topic_model
