import Base from './Base/Base';
import App from './App/App';
import LoginPage from './Login/LoginPage';
import SignupPage from './Signup/SignupPage';
import HistoryPage from './History/HistoryPage';
import Auth from './Auth/Auth';

const routes = {
    component: Base,
    childRoutes: [
        {
            path: '/',
            getComponent: (location, callback) => {
                if (Auth.isUserAuthenticated()) {
                    callback(null, App);
                } 
                else {
                    callback(null, LoginPage);
                }
            }
        },
        {
            path: '/login',
            component: LoginPage
        },
        {
            path: '/signup',
            component: SignupPage
        },
        {
            path: '/logout',
            onEnter: (nextState, replace) => {
                Auth.deauthenticateUser();
                replace('/');
            }
        },
        {
            path: '/history',
            component: HistoryPage
        }
    ]
};

export default routes;