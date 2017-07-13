import pyjsonrpc
import yaml
import os

SERVER_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/server.yaml')

with open(SERVER_CONFIG_FILE, 'r') as serverCfg:
    server_config = yaml.load(serverCfg)

client = pyjsonrpc.HttpClient(url = server_config['rec']['url'])

def getPreferenceForUser(user_id):
    preference_list = client.call('getPreferenceForUser', user_id)
    print "Preference list: %s" % preference_list
    return preference_list