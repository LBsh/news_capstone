var client = require('./rpc_client');

// invoke 'add'
client.add(0, 2, function(response) {
    console.assert(response == 2);
});

client.mul(11, function(response) {
    console.assert(response == 121);
});

// // invoke 'getNewsSummariesForUser'
// client.getNewsSummariesForUser('test', 1, function(response) {
//     console.assert(response != null);
// });

// client.getNewsHistoryForUser('11@11.com', function(response) {
//     console.assert(response != null);
// })

// // invoke 'logNewsClickForUser'
// client.logNewsClickForUser('test', 'test_news');