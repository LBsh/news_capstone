import pyjsonrpc

URL = 'http://localhost:5050'  

client = pyjsonrpc.HttpClient(url = URL)

def getPreferenceForUser(user_id):
    preference_list = client.call('getPreferenceForUser', user_id)
    print "Preference list: %s" % preference_list
    return preference_list