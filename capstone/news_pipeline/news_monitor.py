import os
import sys
import redis
import hashlib
import datetime
import yaml

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import news_api_client
from cloudAMQP_client import CloudAMQPClient

DB_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/databases.yaml')
CLOUDAMQP_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/cloudAMQP.yaml')
NEWS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/news.yaml')

with open(DB_CONFIG_FILE, 'r') as dbCfg:
    db_config = yaml.load(dbCfg)

with open(CLOUDAMQP_CONFIG_FILE, 'r') as amqpCfg:
    cloudAMQP_config = yaml.load(amqpCfg)

with open(NEWS_CONFIG_FILE, 'r') as newsCfg:
    news_config = yaml.load(newsCfg)

# loading configuration from yaml files
redis_client = redis.StrictRedis(db_config['redis']['host'], db_config['redis']['port'])
cloudAMQP_client = CloudAMQPClient(cloudAMQP_config['url'], cloudAMQP_config['scrape_queue_name'])

while True:
    news_list = news_api_client.getNewsFromSources(news_config['news_sources'])
    num_of_new_news = 0

    for news in news_list:
        news_digest = hashlib.md5(news['title'].encode('utf-8')).digest().encode('base64')

        if redis_client.get(news_digest) is None:
            num_of_new_news = num_of_new_news + 1
            news['digest'] = news_digest

            # If 'publishedAt' is None, set it to current UTC time
            if news['publishedAt'] is None:
                # Make the time in format YYYY-MM-DDTHH:MM:SSZ in UTC
                news['publishedAt'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

            redis_client.set(news_digest, news)
            redis_client.expire(news_digest, db_config['redis']['time_out_in_seconds'])

            cloudAMQP_client.sendMessage(news)

    print "Fetched %d news." % num_of_new_news

    cloudAMQP_client.sleep(cloudAMQP_config['monitor_sleep_time'])