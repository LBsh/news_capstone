import os
import re
import sys
import yaml

from newspaper import Article

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

import cnn_news_scraper
from cloudAMQP_client import CloudAMQPClient

CLOUDAMQP_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/cloudAMQP.yaml')

with open(CLOUDAMQP_CONFIG_FILE, 'r') as amqpCfg:
    cloudAMQP_config = yaml.load(amqpCfg)

scrape_news_queue_client = CloudAMQPClient(cloudAMQP_config['url'], cloudAMQP_config['scrape_queue_name'])
dedupe_news_queue_client = CloudAMQPClient(cloudAMQP_config['url'], cloudAMQP_config['dedupe_queue_name'])

# for every 'cnn' message received from news-scraper-task queue
# xpath the text of the news and add it back to the message
# and send over to news-dedupe-task queue
def handle_message(msg):
    if msg is None or not isinstance(msg, dict):
        print 'message is broken!'
        return

    task = msg
    text = ''
    
    article = Article(task['url'])
    article.download()
    article.parse()


    task['text'] = article.text

    dedupe_news_queue_client.sendMessage(task)


while True:
    if scrape_news_queue_client is not None:
        msg = scrape_news_queue_client.getMessage()
        if msg is not None:
            # Parse and process the task
            try:
                handle_message(msg)
            except Exception as e:
                print e
                pass
        scrape_news_queue_client.sleep(cloudAMQP_config['fetcher_sleep_time'])