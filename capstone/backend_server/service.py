import os
import yaml
import pyjsonrpc
import operations

SERVER_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/server.yaml')

with open(SERVER_CONFIG_FILE, 'r') as serverCfg:
    server_config = yaml.load(serverCfg)

SERVER_HOST = server_config['news_service']['host']
SERVER_PORT = server_config['news_service']['port']


class RequestHandler(pyjsonrpc.HttpRequestHandler):
    """  Test Method """
    @pyjsonrpc.rpcmethod
    def add(self, a, b):
        print "add is called with %d and %d" % (a, b)
        return a + b
    
    """ Get news summaries for a user """
    @pyjsonrpc.rpcmethod
    def getNewsSummariesForUser(self, user_id, page_num):
        return operations.getNewsSummariesForUser(user_id, page_num)

    """ Log news click for a user """
    @pyjsonrpc.rpcmethod
    def logNewsClickForUser(self, user_id, news_id):
        return operations.logNewsClickForUser(user_id, news_id)
        

# Threading Http Server
http_server = pyjsonrpc.ThreadingHttpServer(
    server_address = (SERVER_HOST, SERVER_PORT),
    RequestHandlerClass = RequestHandler
)

print "Starting HTTP server on %s : %d" % (SERVER_HOST, SERVER_PORT)

http_server.serve_forever()