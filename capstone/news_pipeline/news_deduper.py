# -*- coding: utf-8 -*-

import os
import sys
import datetime
import yaml

from dateutil import parser
from sklearn.feature_extraction.text import TfidfVectorizer

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

import mongodb_client
import news_topic_modeling_service_client
from cloudAMQP_client import CloudAMQPClient

# loading configuration from yaml files
NEWS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/news.yaml')
DB_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/databases.yaml')
CLOUDAMQP_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/cloudAMQP.yaml')

with open(DB_CONFIG_FILE, 'r') as dbCfg:
    db_config = yaml.load(dbCfg)

with open(CLOUDAMQP_CONFIG_FILE, 'r') as amqpCfg:
    cloudAMQP_config = yaml.load(amqpCfg)

with open(NEWS_CONFIG_FILE, 'r') as newsCfg:
    news_config = yaml.load(newsCfg)

NEWS_TABLE_NAME = db_config['mongodb_backend']['write_news_table']

dedupe_news_queue_client = CloudAMQPClient(cloudAMQP_config['url'], cloudAMQP_config['dedupe_queue_name'])

def handle_message(msg):
    if msg is None or not isinstance(msg, dict):
        return
    
    task = msg
    text = task['text'].encode('utf-8', 'ignore')
    if text == '':
        print 'Message has not text!'
        return
    
    # get all recent news based on publishedAt
    published_at = parser.parse(task['publishedAt'])
    published_at_day_begin = datetime.datetime(
                             published_at.year,
                             published_at.month,
                             published_at.day,
                             0, 0, 0, 0)

    published_at_day_end = published_at_day_begin + datetime.timedelta(days = 1)

    db = mongodb_client.get_db()
    same_day_news_list = list(db[NEWS_TABLE_NAME].find(
        {'publishedAt': {'$gte': published_at_day_begin,
                         '$lt': published_at_day_end}}))

    if same_day_news_list is not None and len(same_day_news_list) > 0:
        documents = [news['text'].encode('utf-8', 'ignore') for news in same_day_news_list]
        documents.insert(0, text)

        # calculate similarity matrix
        tfidf = TfidfVectorizer().fit_transform(documents)
        pairwise_sim = tfidf * tfidf.T

        print pairwise_sim

        rows, _ = pairwise_sim.shape

        for row in range(1, rows):
            if pairwise_sim[row, 0] > news_config['similarity_threshold']:
                print 'Duplicated news. Ignore.'
                return
    
    # when storing publish date in MongoDB, dates have to be tranformed from string to date format
    task['publishedAt'] = parser.parse(task['publishedAt'])

    # Classify news
    # title = task['title']
    # if title is not None:
    #     topic = news_topic_modeling_service_client.classify(title)
    #     task['class'] = topic
        
    db[NEWS_TABLE_NAME].replace_one({'digest': task['digest']}, task, upsert=True)


while True:
    if dedupe_news_queue_client is not None:
        msg = dedupe_news_queue_client.getMessage()
        if msg is not None:
            # Parse and process task
            try:
                handle_message(msg)
            except Exception as e:
                print e
                pass

        dedupe_news_queue_client.sleep(cloudAMQP_config['deduper_sleep_time'])