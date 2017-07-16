import './Base.css';
import React from 'react';
import {Link} from 'react-router';
import PropTypes from 'prop-types';
import Auth from '../Auth/Auth';
import logo from './logo.png';
import NewsPanel from '../NewsPanel/NewsPanel'


const Base = ({children}) => (
    <div>
     <nav className="nav-bar indigo lighten-1">
       <div className="nav-wrapper">
         <a href='/'><img className='brand-logo center' src={logo} alt='logo' /></a>
         <ul id="nav-mobile" className="right">
           {Auth.isUserAuthenticated() ?
             (<div>           
                <li>{Auth.getUsername()}</li>
                <li><Link to="/logout">Log out</Link></li>
              </div>)
              :
             (<div>
                <li><Link to="/login">Log in</Link></li>
                <li><Link to="/signup">Sign up</Link></li>
              </div>)
           }
         </ul>
       </div>
     </nav>
     <br/>
     {children}
   </div>
);

Base.PropTypes = {
    children: PropTypes.object.isRequired
};

export default Base;