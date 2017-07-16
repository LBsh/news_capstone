import 'materialize-css/dist/css/materialize.min.css';
import 'materialize-css/dist/js/materialize.min.js';

import React, { Component } from 'react';
import logo from './logo.png';
import './App.css';

import NewsPanel from '../NewsPanel/NewsPanel';
import History from '../History/History';

class App extends Component {
  render() {
    return (
      <div>
        <div className='container'>
          <NewsPanel />
        </div>
      </div>
    );
  }
}

export default App;
