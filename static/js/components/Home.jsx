import React    from 'react';
import { Link } from 'react-router-dom';

import './css/Home.css';

const Home = () => {
   return (
      <div className='container-home-outer'>
         <div className='container-home-inner'>
         <h3> New Hire Worksheet </h3>
         <br/>
         <p className='home-text'>
            <i>How it do</i><br/>
            Are you a <Link to='/managers'>Manager</Link>? Click
            for the status of your new hire.<br/>
            Are you a <Link to='/worksheet'>Depot Tech</Link>?
            Click for your day-to-day workflow.<br/>
            <br/>
            <i>What it is</i><br/>
            Drop-in replacement for the current Sharepoint sheets
            used by the Talent, Onboarding and Depot teams.<br/>
            My aim was to design the tool I'd most like to use.<br/>
            <br/>
            <i>What it is not</i><br/>
            A completed, full-featured, fully-functional app.<br/>
            <br/>
            - M.G.Carlini
         </p>
         </div>
      </div>
   );
};

export default Home;
