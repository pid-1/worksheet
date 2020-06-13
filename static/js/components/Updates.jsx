import React, { useState, useEffect} from 'react';
import axios from 'axios';

import './css/Updates.css';

const Updates = () => {
   
   const [updates, setUpdates] = useState([]);


   useEffect(() => {
      pullData();
      const interval = setInterval(() => {
         pullData();
      }, 2000);
      return () => clearInterval(interval);
   }, []);


   const pullData = () => {
      axios.get('https://nho.aurelius.org/api/v1/updates')
         .then(res => {
            setUpdates(res.data);
         })
         .catch(error => {
            console.log(error);
         });
   };


   const updatesTable = () => {
      return (
         <table>
         <tbody>
            <tr>
               <th> Key </th>
               <th> Date </th>
               <th> Changes </th>
            </tr>

            {updates.map((rowData, rowNumber) => 
            <tr key={rowNumber}>
               <td> {rowData.key} </td>
               <td> {rowData.date} </td>
               <td>
                  <ul>
                  {JSON.parse(rowData.changes).map((row, n) => {
                     return ( 
                        <li key={rowNumber + '-' + n}>
                           {n+1}) {row[0]} ("{row[1] || 'None'}" -> "{row[2] || 'None'}")
                        </li>
                     );
                  })}
                  </ul>
               </td>
            </tr>
            )}

         </tbody>
         </table>
      );
   };


   return (
      <div className='container-updates-outer'>
      <div className='container-updates-inner'>

         {updates.length === 0 &&
            'Updates go here ... when there are some'}

         {updates.length > 1 &&
            updatesTable()}

      </div>
      </div>
   );
};

export default Updates;
