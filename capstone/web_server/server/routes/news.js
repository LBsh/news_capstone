var express = require('express');
var rpc_client = require('../rpc_client/rpc_client');
var router = express.Router();


// Get news list
router.get('/userId/:userId/pageNum/:pageNum', function(req, res, next) {
    console.log('Fetching news...');
    user_id = req.params['userId'];
    page_num = req.params['pageNum'];

    rpc_client.getNewsSummariesForUser(user_id, page_num, function(response) {
        res.json(response);
    });

});

// Get news history for user
router.get('/history/:userId', function(req, res, next) {
    console.log('Retrieving history for user...');
    user_id = req.params['userId'];
    console.log(user_id);
    rpc_client.getNewsHistoryForUser(user_id, function(response) {
        res.json(response);
    });
});

// post click log
router.post('/userId/:userId/newsId/:newsId', function(req, res, next) {
    console.log('Recording user click...');
    user_id = req.params['userId'];
    news_id = req.params['newsId'];

    rpc_client.logNewsClickForUser(user_id, news_id);
    res.status(200);
})


module.exports = router;
