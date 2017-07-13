var client = require('./rpc_client');

// invoke 'add'
client.add(0, 2, function(response) {
    console.assert(response == 2);
});

// invoke 'getNewsSummariesForUser'
client.getNewsSummariesForUser('test', 1, function(response) {
    console.assert(response != null);
});

// invoke 'logNewsClickForUser'
client.logNewsClickForUser('test', 'test_news');