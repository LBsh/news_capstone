import json
import os
import pickle
import random
import redis
import sys

from bson.json_util import dumps
from datetime import datetime

# import package in a parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client
import news_rec_service_client
from cloudAMQP_client import CloudAMQPClient

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

NEWS_TABLE_NAME = 'news_labeled'
CLICK_LOG_TABLE_NAME = 'click_log'

NEWS_LIMIT = 200
NEWS_PER_PAGE = 10
USER_NEWS_TIME_OUT_IN_SECONDS = 600

CLOUDAMQP_URL = 'amqp://vjyratxw:oKHc1pFbC581r3UyeMLFrRv79dXaetWo@donkey.rmq.cloudamqp.com/vjyratxw'
CLICK_LOG_QUEUE_NAME = 'click-log-task'

redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT, db=0)
cloudAMQP_client = CloudAMQPClient(CLOUDAMQP_URL, CLICK_LOG_QUEUE_NAME)

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

    for news in sliced_news:
        if news['publishedAt'].date() == datetime.today().date:
            news['time'] = 'today'
        if news['class'] == topPreference:
            news['reason'] = 'recommend'
        
    return json.loads(dumps(sliced_news))


def logNewsClickForUser(user_id, news_id):
    message = {'userId': user_id, 'newsId': news_id, 'timestamp': datetime.utcnow()}

    db = mongodb_client.get_db()
    db[CLICK_LOG_TABLE_NAME].insert(message)

    message = {'userId': user_id, 'newsId': news_id, 'timestamp': str(datetime.utcnow())}
    # Send log task to machine learning service for prediction
    cloudAMQP_client.sendMessage(message)