const express = require('express');
const passport = require('passport');
const router = express.Router();
const validator = require('validator');

router.post('/signup', (req, res, next) => {
    const validationResult = validateSignupForm(req.body);
    if (!validationResult.success) {
        console.log('validation result failed');
        return res.status(400).json({
            success: false,
            message: validationResult.message,
            errors: validationResult.errors
        });
    }

    return passport.authenticate('local-signup', (err) => {
        if (err) {
            console.log(err);
            if (err.name === 'MongoError' && err.code === 11000 ) {
                // the 11000 Mongo code is for a duplication email error
                // the 409 HTTP status code is for conflict error
                return res.status(400).json({
                    success: false,
                    message: 'Check the form for errors.',
                    errors: {
                        email: 'This email has already been registered.'
                    }
                });
            }

            return res.status(400).json({
                success: false,
                message: 'Could not process the form.' + err.message
            });
        }

        return res.status(200).json({
            success: true,
            message: 'You have successfully signup up! Now log in to access the news.'
        });
    })(req, res, next);
});

router.post('/login', (req, res, next) => {
    const validationResult = validateLoginForm(req.body);
    if (!validationResult.success) {
        console.log('validation result failed');
        return res.status(400).json({
            success: false,
            message: validationResult.message,
            errors: validationResult.errors
        })
    }
    
    console.log('entering auth.js passport authentication process');
    return passport.authenticate('local-login', (err, token, data) => {
     
        if (err) {
            if (err.name === 'IncorrectCredentialsError') {
                return res.status(400).json({
                    success: false,
                    message: err.message
                })
            }

            return res.status(400).json({
                success: false,
                message: 'Could not process the form.' + err.message
            })
        }

        return res.status(200).json({
            success: true,
            message: 'auth.js: You have successfully logged in!',
            token,
            data: data
        });
    })(req, res, next);
})


function validateSignupForm(payload) {
    console.log(payload);
    const errors = {};
    let isFormValid = true;
    let message = '';

    if (!payload || typeof payload.email !== 'string' || !validator.isEmail(payload.email)) {
        isFormValid = false;
        errors.email = 'Please provide the correct email address.';
    }

    if (!payload || typeof payload.password !== 'string' || payload.password.trim().length < 8) {
        isFormValid = false;
        errors.password = 'Password mus have at least 8 characters.';
    }

    if (!isFormValid) {
        message = 'Check the form for errors';
    }

    return {
        success: isFormValid,
        message,
        errors
    };
}

function validateLoginForm(payload) {
    console.log('auth.js: ' + JSON.stringify({payload}));
    const errors = {};
    let isFormValid = true;
    let message = '';

    if (!payload 
    || typeof payload.email !== 'string'  
    || !validator.isEmail(payload.email) 
    || payload.email.trim().length === 0) {
        isFormValid = false;
        errors.email = 'Please provide the correct email address.';
    }

    if (!payload || typeof payload.password !== 'string' || payload.password.trim().length === 0) {
        isFormValid = false;
        errors.password = 'Please provide your password.';
    }

    if (!isFormValid) {
        message = 'Check the form for errors.';
    }

    console.log('login validation success');
    return {
        success: isFormValid,
        message,
        errors
    };
    
}

module.exports = router;