var express = require('express');
var app = express();
var path = require('path');
var cors = require('cors');
var passport = require('passport');
var bodyParser = require('body-parser');

var auth = require('./routes/auth');
var index = require('./routes/index');
var news = require('./routes/news');

var config = require('../config/config.json')
require('./models/main.js').connect(config.mongodb.url);

// view engine setup
app.set('view engine', 'jade');
app.set('views', path.join(__dirname, '../client/build/'));

app.use('/static', express.static(path.join(__dirname, '../client/build/static')));
app.use(bodyParser.json());

// load passport strategies
app.use(passport.initialize());
var localSignupStrategy = require('./passport/signup_passport');
var localLoginStrategy = require('./passport/login_passport');
passport.use('local-signup', localSignupStrategy);
passport.use('local-login', localLoginStrategy);

// enable cross domain request
app.use(cors());

app.use('/', index);
app.use('/auth', auth);

// pass the authentication checker to middleware
const authCheckerMiddleware = require('./middleware/auth_checker');
app.use('/news', authCheckerMiddleware);
app.use('/news', news);

// catch 404 and forward to error handler
app.use(function(req, res) {
  var err = new Error('Not Found');
  err.status = 404;
  res.send('404 Not Found');
});

module.exports = app;
