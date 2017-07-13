const jwt = require('jsonwebtoken');
const User= require('mongoose').model('User');
const config = require('../../config/config.json');

module.exports = (req, res, next) => {
    // const headers = req.headers;
    // console.log('auth_checker: req: ' + JSON.stringify({headers}));

    if(!req.headers.authorization) {
        console.log('auth checker: user is not authorized');
        return res.status(401).end();
    }

    // get the last part from a authorization header string like "bearer token-value"
    const token = req.headers.authorization.split(' ')[1];


    console.log('auth_checker: token: ' + token);

    // decode the token using a secret key-phrase
    return jwt.verify(token, config.mongodb.jwtSecret, (err, decoded) => {
        if (err) {
            return res.status(401).end();
        }

        const id = decoded.sub;

        // check if user exists
        return User.findById(id, (userErr, user) => {
            if (userErr || !user) {
                return res.status(401).end();
            }
            console.log('auth checker: user is authorized');
            return next();
        });
    }); 
};