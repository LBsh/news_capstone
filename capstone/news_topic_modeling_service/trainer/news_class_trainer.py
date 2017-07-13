import news_cnn_model
import numpy as np
import os
import pandas as pd
import pickle
import shutil
import tensorflow as tf
import yaml
from sklearn import metrics

NEWS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../..', 'config/news.yaml')

with open(NEWS_CONFIG_FILE, 'r') as newsCfg:
    news_config = yaml.load(newsCfg)

learn = tf.contrib.learn

MODEL_OUTPUT_DIR = '../model/'
DATA_SET_FILE = '../training_data/labeled_news.csv'
VARS_FILE = '../model/vars'
VOCAB_PROCESSOR_SAVE_FILE = '../model/vocab_processor_save_file'
MAX_DOCUMENT_LENGTH = news_config['max_doc_length']
N_CLASSES = news_config['num_of_classes']
TRAINING_END_INDEX = news_config['training_end_index']

# Training params
STEPS = news_config['steps']

def main(unused_argv):
    if news_config['remove_previous_model']:
        # Remove old model
        shutil.rmtree(MODEL_OUTPUT_DIR)
        os.mkdir(MODEL_OUTPUT_DIR)

    # Prepare training and testing data
    df = pd.read_csv(DATA_SET_FILE, header=None)

    train_df = df[0:TRAINING_END_INDEX]
    test_df = df.drop(train_df.index)

    # x - news title, y - class
    x_train = train_df[2]
    y_train = train_df[0]
    x_test = test_df[2]
    y_test = test_df[0]

    # Process vocabulary
    vocab_processor = learn.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH)
    x_train = np.array(list(vocab_processor.fit_transform(x_train)))
    x_test = np.array(list(vocab_processor.transform(x_test)))

    n_words = len(vocab_processor.vocabulary_)
    print('Total words: %d' % n_words)

    # Saving n_words and vocab_processor:
    with open(VARS_FILE, 'w') as f:
        pickle.dump(n_words, f)

    vocab_processor.save(VOCAB_PROCESSOR_SAVE_FILE)

    # Build model
    classifier = learn.Estimator(
        model_fn=news_cnn_model.generate_cnn_model(N_CLASSES, n_words),
        model_dir=MODEL_OUTPUT_DIR)

    # Train and predict
    classifier.fit(x_train, y_train, steps=STEPS)

    # Evaluate model
    y_predicted = [
        p['class'] for p in classifier.predict(x_test, as_iterable=True)
    ]
    
    print y_predicted

    score = metrics.accuracy_score(y_test, y_predicted)
    print('Accuracy: {0:f}'.format(score))

if __name__ == '__main__':
    tf.app.run(main=main)