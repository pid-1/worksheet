import React       from 'react';
import { NavLink } from 'react-router-dom';

import Logo from './nhoLogo.svg';

import './css/NavBar.css';

const NavBar = () => {

   return (
      <nav className='container-nav-outer'>
         <div>
         <NavLink className='nav-image' to='/'>
            <Logo width='70%' height='65%'/>
         </NavLink>
         </div>

         <ul className='container-nav-links'>
            <NavLink to='/worksheet'
                     className='nav-link'
                     activeClassName='nav-link-active'>
               <li> Worksheet </li>
            </NavLink>

            <NavLink to='/managers'
                     activeClassName='nav-link-active'
                     className='nav-link'>
               <li> Managers </li>
            </NavLink>

            <NavLink to='/updates'
                     className='nav-link'
                     activeClassName='nav-link-active'>
               <li> Updates </li>
            </NavLink>

            <NavLink to='/settings'
                     className='nav-link'
                     activeClassName='nav-link-active'>
               <li> Settings </li>
            </NavLink>
         </ul>
      </nav>
   );

};

export default NavBar;
