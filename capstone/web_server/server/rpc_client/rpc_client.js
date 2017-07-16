var jayson = require('jayson');
var yaml = require('js-yaml');
var fs = require('fs');

// full path has to be used due to discrepancy between path convention
var server_config = yaml.safeLoad(fs.readFileSync(__dirname + '/../../../config/server.yaml', 'utf8'));

var client = jayson.client.http({
    port: server_config.news_service.port,
    hostname: server_config.news_service.host
});

// Test RPC method
function add(a, b, callback) {
    client.request('add', [a, b], function(err, error, response) {
        if(err) throw err;
        console.log(response);
        callback(response);
    });
}

function mul(a, callback) {
    client.request('mul', [a], function(err, error, response) {
        if(err) throw err;
        console.log(response);
        callback(response);
    });
}

function getNewsSummariesForUser(user_id, page_num, callback) {
    client.request('getNewsSummariesForUser', [user_id, page_num], function(err, error, response) {
        if (err) throw err;
        callback(response);
    })
}

function getNewsHistoryForUser(user_id, callback) {
    client.request('getNewsHistoryForUser', [user_id], function(err, error, response) {
        if (err) throw err;
        callback(response);
    })
}

function logNewsClickForUser(user_id, news_id) {
    client.request('logNewsClickForUser', [user_id, news_id], function(err, error, response) {
        if (err) throw err;
    })
}

module.exports = {
    add: add,
    mul: mul,
    getNewsSummariesForUser: getNewsSummariesForUser,
    logNewsClickForUser: logNewsClickForUser,
    getNewsHistoryForUser: getNewsHistoryForUser
};