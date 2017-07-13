import React from 'react';
import PropTypes from 'prop-types';
import Auth from '../Auth/Auth';
import LoginForm from './LoginForm';

class LoginPage extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.state = {
            errors: {},
            user: {
                email:'',
                password: ''
            }
        };

        this.processForm = this.processForm.bind(this);
        this.userChange = this.userChange.bind(this);
    }

    processForm(event) {
        event.preventDefault();

        const email = this.state.user.email;
        const password = this.state.user.password;

        console.log('email from loginpage: ' + email);
        console.log('password: ' + password);

        // Post login data and handle response
        fetch('http://localhost:3000/auth/login', {
            method: 'POST',
            cache: false,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body:JSON.stringify ({
                email: this.state.user.email,
                password: this.state.user.password
            })
        }).then(response => {
            if (response.status === 200) {
                console.log('success from login page!!');

                response.json().then(function(json) {
                    console.log(json);
                    Auth.authenticateUser(json.token, email);
                    this.context.router.replace('/');
                }.bind(this));
            } else {
                console.log('login failed');
                response.json().then(function(json) {
                    const errors = json.errors? json.errors : {};
                    errors.summary = json.message;
                    this.setState({errors});
                }.bind(this));
            }
        });
    }

    userChange(event) {
        const field = event.target.name;
        const user = this.state.user;
        user[field] = event.target.value;

        this.setState({user});
    }

    render() {
        return (
            <LoginForm
            onSubmit = {this.processForm}
            onChange = {this.userChange}
            errors = {this.state.errors}
            />
        )
    }
}

// To make react-router work
LoginPage.contextTypes = {
    router: PropTypes.object.isRequired
}

export default LoginPage;