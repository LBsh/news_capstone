# -*- coding: utf-8 -*-

"""
Time decay model:
If selected:
p = (1-α)p + α
If not:
p = (1-α)p
Where p is the selection probability, and α is the degree of weight decrease.
The result of this is that the nth most recent selection will have a weight of
(1-α)^n. Using a coefficient value of 0.05 as an example, the 10th most recent
selection would only have half the weight of the most recent. Increasing epsilon
would bias towards more recent results more.
"""

import os
import sys
import yaml

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client
from cloudAMQP_client import CloudAMQPClient

DB_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/databases.yaml')
NEWS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/news.yaml')
CLOUDAMQP_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/cloudAMQP.yaml')

with open(DB_CONFIG_FILE, 'r') as dbCfg:
    db_config = yaml.load(dbCfg)
    
with open(NEWS_CONFIG_FILE, 'r') as newsCfg:
    news_config = yaml.load(newsCfg)

with open(CLOUDAMQP_CONFIG_FILE, 'r') as amqpCfg:
    cloudAMQP_config = yaml.load(amqpCfg)

NUM_OF_CLASSES = news_config['num_of_classes']
INITIAL_P = 1.0 / NUM_OF_CLASSES
ALPHA = news_config['alpha']
NEWS_CLASSES = news_config['classes']

PREFERENCE_MODEL_TABLE_NAME = db_config['mongodb']['preference_model_table']
NEWS_TABLE_NAME = db_config['mongodb']['read_news_table']

cloudAMQP_client = CloudAMQPClient(cloudAMQP_config['url'], cloudAMQP_config['click_log_queue_name'])

def handle_msg(msg):
    if msg is None or not isinstance(msg, dict):
        print 'Invalid message!!'
        return

    if ('userId' not in msg
        or 'newsId' not in msg
        or 'timestamp' not in msg):
        print 'Message does not contain necessary info'
        return

    userId = msg['userId']
    newsId = msg['newsId']

    # Update user's preference
    db = mongodb_client.get_db()
    model = db[PREFERENCE_MODEL_TABLE_NAME].find_one({'userId': userId})

    # If model does not exist, create a new one
    if model is None:
        print 'New user... Creating preference model for user: %s' % userId
        new_model = {'userId': userId}
        preference = {}
        for i in NEWS_CLASSES:
            preference[i] = float(INITIAL_P)
        new_model['preference'] = preference
        model = new_model
        
    print 'Updating preference model for user: %s' % userId

    # Update the model using time decay method
    news = db[NEWS_TABLE_NAME].find_one({'digest': newsId})
    if (news is None
        or 'class' not in news
        or news['class'] not in NEWS_CLASSES):
        print news is None
        print 'class' not in news
        print news['class'] not in NEWS_CLASSES
        return

    click_class = news['class']

    # Update the clicked one
    old_p = model['preference'][click_class]
    model['preference'][click_class] = float((1-ALPHA) * old_p + ALPHA)

    # Update not clicked ones
    for i, prob in model['preference'].iteritems():
        if not i == click_class:
            model['preference'][i] = float((1-ALPHA) * model['preference'][i])

    db[PREFERENCE_MODEL_TABLE_NAME].replace_one({'userId': userId}, model, upsert = True)


def run():
    while True:
        if cloudAMQP_client is not None:
            msg = cloudAMQP_client.getMessage()
            if msg is not None:
                # Parse and process the task
                try:
                    handle_msg(msg)
                except Exception as e:
                    print e
                    pass
            # Remove if becoming a bottleneck
            cloudAMQP_client.sleep(cloudAMQP_config['click_log_sleep_time'])

if __name__ == "__main__":
    run()