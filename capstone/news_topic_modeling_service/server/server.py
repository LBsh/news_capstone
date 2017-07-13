import numpy as np
import os
import pandas as pd
import pickle
import pyjsonrpc
import sys
import tensorflow as tf
import time
import yaml

from tensorflow.contrib.learn.python.learn.estimators import model_fn
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# import packages in trainer
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'trainer'))
import news_cnn_model

NEWS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../..', 'config/news.yaml')
SERVER_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../..', 'config/server.yaml')

with open(NEWS_CONFIG_FILE, 'r') as newsCfg:
    news_config = yaml.load(newsCfg)

with open(SERVER_CONFIG_FILE, 'r') as serverCfg:
    server_config = yaml.load(serverCfg)

SERVER_HOST = server_config['topic_modeling']['host']
SERVER_PORT = server_config['topic_modeling']['port']

learn = tf.contrib.learn

VARS_FILE = '../model/vars'
VOCAB_PROCESSOR_SAVE_FILE = '../model/vocab_processor_save_file'

MODEL_DIR = '../model'

MODEL_UPDATE_LAG_IN_SECONDS = news_config['update_lag_in_seconds']
N_CLASSES = news_config['num_of_classes']
CLASS_MAP = news_config['class_map']
MAX_DOCUMENT_LENGTH = news_config['max_doc_length']
TRAINING_END_INDEX = news_config['training_end_index']
N_WORDS = news_config['n_words']

vocab_processor = None

classifier = None

def restoreVars():
    with open(VARS_FILE, 'r') as f:
        global N_WORDS
        N_WORDS = pickle.load(f)
    global vocab_processor
    vocab_processor = learn.preprocessing.VocabularyProcessor.restore(VOCAB_PROCESSOR_SAVE_FILE)
    print vocab_processor
    print 'Vars updated.'

def loadModel():
    global classifier
    classifier = learn.Estimator(
        model_fn=news_cnn_model.generate_cnn_model(N_CLASSES, N_WORDS),
        model_dir=MODEL_DIR)
    # Prepare training and testing
    df = pd.read_csv('../training_data/labeled_news.csv', header=None)

    # TODO: fix this until https://github.com/tensorflow/tensorflow/issues/5548 is solved.
    # We have to call evaluate or predict at least once to make the restored Estimator work.
    train_df = df[0:TRAINING_END_INDEX]
    x_train = train_df[2]
    x_train = np.array(list(vocab_processor.transform(x_train)))
    y_train = train_df[0]
    classifier.evaluate(x_train, y_train)

    print "Model updated."

restoreVars()
loadModel()

print "Model loaded"

class ReloadModelHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        # Reload model
        print "Model update detected. Loading new model."
        time.sleep(MODEL_UPDATE_LAG_IN_SECONDS)
        restoreVars()
        loadModel()


class RequestHandler(pyjsonrpc.HttpRequestHandler):
    @pyjsonrpc.rpcmethod
    def classify(self, text):
        text_series = pd.Series([text])
        predict_x = np.array(list(vocab_processor.transform(text_series)))
        print predict_x

        y_predicted = [
            p['class'] for p in classifier.predict(
                predict_x, as_iterable=True)
        ]
        print y_predicted[0]
        topic = CLASS_MAP[str(y_predicted[0])]
        return topic

# Setup watchdog
observer = Observer()
observer.schedule(ReloadModelHandler(), path=MODEL_DIR, recursive=False)
observer.start()

# Threading HTTP-Server
http_server = pyjsonrpc.ThreadingHttpServer(
    server_address = (SERVER_HOST, SERVER_PORT),
    RequestHandlerClass = RequestHandler
)

print "Starting predicting server ..."
print "URL: http://" + str(SERVER_HOST) + ":" + str(SERVER_PORT)

http_server.serve_forever()