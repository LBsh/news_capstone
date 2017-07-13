import yaml
import os

from pymongo import MongoClient

DB_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/databases.yaml')

with open(DB_CONFIG_FILE, 'r') as dbCfg:
    db_config = yaml.load(dbCfg)

MONGO_DB_HOST = db_config['mongodb']['host']
MONGO_DB_PORT = db_config['mongodb']['port']
DB_NAME = db_config['mongodb']['db_name']

client = MongoClient("%s:%s" % (MONGO_DB_HOST, MONGO_DB_PORT))

def get_db(db=DB_NAME):
    db = client[db]
    return db

    