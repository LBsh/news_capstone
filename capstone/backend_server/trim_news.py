# this is a one-time-use file to trim news in mongodb

import os
import sys
import json
import pickle
from bson.json_util import dumps

# import package in a parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client

UNTRIMMED_NEWS_TABLE_NAME = 'news'
TRIMMED_NEWS_TABLE_NAME = 'news_trimmed'

def trimNews():
    db = mongodb_client.get_db()
    all_untrimmed_news = list(db[UNTRIMMED_NEWS_TABLE_NAME].find().sort([('publishedAt', -1)]))
    num_of_news = 0

    for news in all_untrimmed_news:
        if (news is not None
            and 'description' in news
            and 'title' in news
            and 'url' in news
            and news['source'] != 'focus'):
            trimmed_news = {}
            trimmed_news['description'] = news['description']
            trimmed_news['title'] = news['title']
            trimmed_news['url'] = news['url']
            trimmed_news['source'] = news['source']
            db[TRIMMED_NEWS_TABLE_NAME].insert_one(trimmed_news)
            num_of_news = num_of_news + 1

    print 'trimmed %s news' % num_of_news

if __name__ == "__main__":
    trimNews()