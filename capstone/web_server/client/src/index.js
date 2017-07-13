import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import routes from './routes';
import { Router, browserHistory } from 'react-router';

ReactDOM.render(
    <Router history={browserHistory} routes={routes} />, 
    document.getElementById('root')
);