const jwt = require('jsonwebtoken');
const User = require('mongoose').model('User');
const PassportLocalStrategy = require('passport-local').Strategy;
const config = require('../config/config.json');

module.exports = new PassportLocalStrategy({
    usernameField: 'email',
    passwordField: 'password',
    passReqToCallback: true
}, (req, email, password, done) => {

    const userData = {
        email: email.trim(),
        password: password.trim()
    };

    const newUser = new User(userData);
    newUser.save((err) => {
        if (err) { return done(err); }
        console.log('Save new user!');
        return done(null);3
    });
})