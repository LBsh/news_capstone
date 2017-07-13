import pyjsonrpc
import os
import operator
import sys
import yaml

# import file from common package
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client

# start mongodb before running

DB_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/databases.yaml')
SERVER_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/server.yaml')

with open(DB_CONFIG_FILE, 'r') as dbCfg:
    db_config = yaml.load(dbCfg)

with open(SERVER_CONFIG_FILE, 'r') as serverCfg:
    server_config = yaml.load(serverCfg)

PREFERENCE_MODEL_TABLE_NAME = db_config['mongodb_backend']['preference_model_table']
SERVER_HOST = server_config['rec']['host']
SERVER_PORT = server_config['rec']['port']

# Ref: https://www.python.org/dev/peps/pep-0485/#proposed-implementation
# Ref: http://stackoverflow.com/questions/5595425/what-is-the-best-way-to-compare-floats-for-almost-equality-in-python
def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

class RequestHandler(pyjsonrpc.HttpRequestHandler):
    """ Get user's preference in an ordered class list """
    @pyjsonrpc.rpcmethod
    def getPreferenceForUser(self, user_id):
        db = mongodb_client.get_db()
        model = db[PREFERENCE_MODEL_TABLE_NAME].find_one({'userId': user_id})
        
        if model is None:
            return []

        sorted_tuples = sorted(model['preference'].items(), key = operator.itemgetter(1), reverse = True)
        sorted_list = [x[0] for x in sorted_tuples]
        sorted_value = [x[1] for x in sorted_tuples]

        if isclose(float(sorted_value[0]), float(sorted_value[-1])):
            return []

        return sorted_list

# Threading HTTP Server
http_server = pyjsonrpc.ThreadingHttpServer(
    server_address = (SERVER_HOST, SERVER_PORT),
    RequestHandlerClass = RequestHandler
)

print "Starting HTTP server on %s:%d" % (SERVER_HOST, SERVER_PORT)

http_server.serve_forever()
