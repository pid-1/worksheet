import React, { useState } from 'react';
import axios from 'axios';

import './css/SignIn.css';

const SignIn = ({ setIsAuthenticated, setView, setTheme }) => {

   const [errors, setErrors] = useState();

   // Verifies userid/password against the DB
   const logIn = event => {
      let userid = event.target.userid.value;
      let password = event.target.password.value;

      axios({
         method: 'post',
         url: 'https://nho.aurelius.org/login',
         data:
            {
               userid: userid,
               password: password
            }
      })
         .then(res => {
            try {
               let u = JSON.parse(res.data);

               if (u.view) {
                  console.log('DEFAULTS.view:', u.view);
                  setView(u.view);
               }
               if (u.theme) {
                  console.log('DEFAULTS.theme:', u.theme);
                  setTheme(u.theme);
               }
            } catch(error) {
               console.log(error);
            } finally {
               setIsAuthenticated(true);
            }
         })
         .catch(err => {
            setErrors(err.response);
         });

      event.preventDefault();
   };


   return ( 
      <div className='container-form-outer'>
         <div className='container-form-inner'>
         
         <br/>
         <h3> Authentication Required </h3>
         <br/>

         <form onSubmit={logIn}>
            <input autoFocus type='text' id='userid' placeholder=' userid' autoComplete='off' />
            <input type='password' id='password' placeholder=' password' autoComplete='off' />
            <button type='submit'> Submit </button>
         </form>

         <br/>

         {errors && <p className='errors'> Status:  {errors.status}<br/>Error:  {errors.data || errors.statusText} </p>}
         </div>
      </div>
   );
};

export default SignIn;
