import React from 'react';
import PropTypes from 'prop-types';
import SignupForm from './SignupForm';

class SignupPage extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.state = {
            errors: {},
            user: {
                email:'',
                password: '',
                confirm_password: ''
            }
        };

        this.processForm = this.processForm.bind(this);
        this.userChange = this.userChange.bind(this);
    }

    processForm(event) {
        event.preventDefault();

        const email = this.state.user.email;
        const password = this.state.user.password;
        const confirm_password = this.state.user.confirm_password;

        console.log('email: ' + email);
        console.log('password: ' + password);
        console.log('confirm password: ' + confirm_password);

        if (password !== confirm_password) {
            console.log('password not matching from processForm');
            return;
        }

        // post signup info and handle response
        fetch('http://localhost:3000/auth/signup', {
            method: 'POST',
            cache: false,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: this.state.user.email,
                password: this.state.user.password
            })
        }).then(response => {
            if (response.status === 200) {
                this.setState({
                    errors: {}
                });

                // change the current page to /login
                this.context.router.replace('/login');
            } else {
                console.log('signup failed');
                response.json().then(function(json) {
                    const errors = json.errors? json.errors : {};
                    errors.summary = json.message;
                    console.log(this.state.errors);
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

        if (this.state.user.password !== this.state.user.confirm_password) {
            const errors = this.state.errors;
            errors.password = "Password does not match";
            this.setState({errors});
        } else {
            const errors = this.state.errors;
            errors.password = '';
            this.setState({errors});
        }   
    }

    render() {
        return (
            <SignupForm
            onSubmit = {this.processForm}
            onChange = {this.userChange}
            errors = {this.state.errors}
            />
        )
    }
}

// to make react-router work
SignupPage.contextTypes = {
    router: PropTypes.object.isRequired
};

export default SignupPage;