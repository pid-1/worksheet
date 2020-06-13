import React from 'react';

import './css/Settings.css';

const Settings = ({ setView, setTheme }) => {

   const formHandler = e => {
      let view = e.target.view.value;
      let theme = e.target.theme.value;

      if (view) {
         setView(view);
         console.log('new view--', view);
      }
      if (theme) {
         setTheme(theme);
         console.log('new theme--', theme);
      }

      e.preventDefault();
   };


   return (
      <div className='container-settings-outer'>
      <div className='container-settings-inner'>

         <h3> View </h3>
         <br/>
         <form className='form-settings' onSubmit={formHandler}>
            <div className='form-settings-content'>
            <input type='radio' name='view' id='depot' value='depot'/>
            <label htmlFor='depot'> Depot </label>

            <input type='radio' name='view' value='onboarding' id='onboarding'/>
            <label htmlFor='onboarding'> Onboarding </label>

            <input type='radio' name='view' value='all' id='all'/>
            <label htmlFor='all'> All </label>
            </div>

            <br/><br/>
            <h3> Worksheet Theme </h3>
            <br/>

            <div className='form-settings-content'>
            <input type='radio' name='theme' value='ag-theme-balham' id='light'/>
            <label htmlFor='light'> Light </label>

            <input type='radio' name='theme' value='ag-theme-balham-dark' id='dark'/>
            <label htmlFor='dark'> Dark </label>
            </div>
            <br/><br/>

            <button type='submit'> Submit </button>
            
         </form>

      </div>
      </div>
   );
};

export default Settings;
