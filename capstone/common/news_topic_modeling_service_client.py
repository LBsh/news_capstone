import pyjsonrpc
import yaml
import os

SERVER_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/server.yaml')

with open(SERVER_CONFIG_FILE, 'r') as serverCfg:
    server_config = yaml.load(serverCfg)

client = pyjsonrpc.HttpClient(url = server_config['topic_modeling']['url'])

def classify(text):
    topic = client.call('classify', text)
    print "Topic: %s" % str(topic)
    return topic