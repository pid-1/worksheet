import React, { useState, useEffect} from 'react';
import axios from 'axios';

import HireDetails from './HireDetails';

import './css/Managers.css';

const Managers = () => {
   
   const [hireInfo, setHireInfo] = useState([]);
   const [hireLoading, setHireLoading] = useState(true);

   useEffect(() => {
      if (hireInfo.length < 1) {
         return;
      }
      setHireLoading(false);
   }, [hireInfo]);


   const getInfo = e => {
      let req = e.target.req.value;

      axios.get('https://nho.aurelius.org/api/v1/worksheet', {
            params: {
               view: 'managers',
               req: req
            }
         })
         .then(res => {
            if (res.data !== null) {
               setHireInfo(res.data);
            } else {
               console.log('hire not found');
            }
         })
         .catch(error => {
            console.log(error);
         });

      e.preventDefault();
   };

   const instructions = () => {
      return (
         <p style={{ color: '#333' }}>
            Enter the Requisition # for your hire
            to see more detailed information, and
            any potential action items.
         </p>
      );
   };

   return (
      <div className='container-managers-outer'>

         <div className='container-managers-left'>
            <form onSubmit={getInfo}>
               <label htmlFor='req'> Requisition: </label>
               <input type='text' id='req' placeholder=' #' autoComplete='off'/>
               {/* <button type='submit'> search </button> */}

               {/* EDIT
               <p>
                  Put section here with a rundown of the workflow:<br/>
                  <br/>
                  Use the link from inside.corp for the manager's checklist
               </p>
               */}

            </form>
         </div>

         <div className='container-managers-right'>
            {hireLoading && instructions()}
            {hireLoading || <HireDetails hireInfo={hireInfo} />}
         </div>

      </div>
   );
};

export default Managers
