import json
import os
import pickle
import random
import redis
import sys
import yaml
import logging.config

from bson.json_util import dumps
from datetime import datetime
from operator import itemgetter

# import package in a parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client
import news_rec_service_client
from cloudAMQP_client import CloudAMQPClient

NEWS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/news.yaml')
DB_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/databases.yaml')
CLOUDAMQP_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/cloudAMQP.yaml')
LOGGING_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/logging.yaml')

with open(LOGGING_CONFIG_FILE, 'r') as loggingCfg:
    logging_config = yaml.load(loggingCfg)
    logging.config.dictConfig(logging_config)
    
with open(DB_CONFIG_FILE, 'r') as dbCfg:
    db_config = yaml.load(dbCfg)

with open(CLOUDAMQP_CONFIG_FILE, 'r') as amqpCfg:
    cloudAMQP_config = yaml.load(amqpCfg)

with open(NEWS_CONFIG_FILE, 'r') as newsCfg:
    news_config = yaml.load(newsCfg)

REDIS_HOST = db_config['redis']['host']
REDIS_PORT = db_config['redis']['port']

NEWS_TABLE_NAME = db_config['mongodb']['read_news_table']
CLICK_LOG_TABLE_NAME = db_config['mongodb']['click_log_table']

NEWS_CLASSES = news_config['classes']
NEWS_LIMIT = news_config['read_news_limit']
NEWS_PER_PAGE = news_config['news_per_page']
USER_NEWS_TIME_OUT_IN_SECONDS = news_config['user_timeout_in_seconds']

redis_client = redis.StrictRedis(db_config['redis']['host'], 
                                 db_config['redis']['port'], 
                                 db = db_config['redis']['strict_db'])
cloudAMQP_client = CloudAMQPClient(cloudAMQP_config['url'], cloudAMQP_config['click_log_queue_name'])

def getNewsSummariesForUser(user_id, page_num):
    page_num = int(page_num)
    begin_index = (page_num - 1) * NEWS_PER_PAGE
    end_index = page_num * NEWS_PER_PAGE

    # The final list of news to be returned
    sliced_news = []

    if redis_client.get(user_id) is not None:
        print 'Pulling page %s from Redis...' % page_num
        news = pickle.loads(redis_client.get(user_id))

        # If begin_index is out of range, this will return empty list;
        # If end_index is out of range (begin_index is within the range), this
        # will return all remaining news ids.
        sliced_news = news[begin_index:end_index]
        if sliced_news == []:
            print 'no news to be returned!!!'
    else:
        db = mongodb_client.get_db()
        total_news = list(db[NEWS_TABLE_NAME].find().sort([('publishedAt', -1)]).limit(NEWS_LIMIT))

        for news in total_news:
            del news['text']
            
        redis_client.set(user_id, pickle.dumps(total_news))
        redis_client.expire(user_id, USER_NEWS_TIME_OUT_IN_SECONDS)

        sliced_news = total_news[begin_index:end_index]

    preference_list = news_rec_service_client.getPreferenceForUser(user_id)
    topPreference = None

    if preference_list is not None and len(preference_list) > 0:
        print 'User has preference. Identifying top preference...'
        topPreference = preference_list[0]
        preference_order = { key: i for i, key in enumerate(preference_list)}
        sliced_news = sorted(sliced_news, key = lambda d: preference_order[d['class']])
        print 'Sorting complete.'

    for news in sliced_news:
        if news['publishedAt'].date() == datetime.today().date:
            news['time'] = 'today'
        if (news is None
            or 'class' not in news):
            logging.error(news is None, exc_info = True)
            logging.error('class' not in news, exc_info = True)
            
        elif news['class'] == topPreference:
            news['reason'] = 'recommend'
        
    return json.loads(dumps(sliced_news))


def getNewsHistoryForUser(user_id):
    print 'getting news history from mongodb...'
    history_news = []

    db = mongodb_client.get_db()
    click_log = map(itemgetter('newsId'),list(db[CLICK_LOG_TABLE_NAME].find({'userId': user_id}, {'newsId':1})))
    print click_log
    history_news = list(db[NEWS_TABLE_NAME].find({'digest': {'$in': click_log}}))

    return json.loads(dumps(history_news))


def logNewsClickForUser(user_id, news_id):
    message = {'userId': user_id, 'newsId': news_id, 'timestamp': datetime.utcnow()}

    db = mongodb_client.get_db()
    db[CLICK_LOG_TABLE_NAME].insert(message)

    message = {'userId': user_id, 'newsId': news_id, 'timestamp': str(datetime.utcnow())}
    # Send log task to machine learning service for prediction
    cloudAMQP_client.sendMessage(message)