import React from 'react';

import './css/HireDetails.css';

const HireDetails = ({ hireInfo }) => {

   let good = '\u2713';
   let bad  = 'x';

   //--| hire status |--//
   // offer extended, hired, etc.
   let v_hire_status;
      if (hireInfo['hire_status'] === '5 - hired') {
         v_hire_status = good;
      } else {
         v_hire_status = bad;
      }

   //--| depot status |--//
   // sheet printed, in progress, ready, etc..
   let v_depot_status;
      if (hireInfo['depot_status'] === 'ready') {
            v_depot_status = good;
      } else {
            v_depot_status = bad;
      }

   //--| ticket info |--//
   //  - # tickets placed
   //  - link to order form if no tickets
   let v_tickets_found;
   let v_tickets_link = () => {
      return (
         <a href='https://adobe.service-now.com/sc?id=sc_cat_item&sys_id=34d64a694f1e1f00012f2dfe0310c7d0'
            target="_blank" rel="noopener noreferrer">
            Order Here
         </a>
      );
   };
   let numTickets;

   if (hireInfo['tickets_found'] === null) {
      numTickets = 0;
   } else {
      numTickets = hireInfo['tickets_found'].split(',').length
   }

   if (numTickets === 1) {
         v_tickets_found = good;
   } else {
         v_tickets_found = bad;
   }


   const actionItemsTable = () => {
      return (
         <table>
         <tbody>
            <tr>
               <td> Hire Status </td>
               <td> {v_hire_status} </td>
               <td> {v_hire_status === 'x' && 'Contact talent coordinator'} </td> 
            </tr>
            <tr>
               <td> Ticket(s) Found:  {numTickets} </td>
               <td> {v_tickets_found}  </td>
               <td> {numTickets === 0 && v_tickets_link()} </td>
            </tr>
            <tr>
               <td> Computer Status </td>
               <td> {v_depot_status} </td>
               <td> {v_depot_status === 'x' && 'Contact Depot DL'} </td>
            </tr>
         </tbody>
         </table>
      );
   };


   const detailsTable = () => {
      return (
         <table>
         <tbody>
            <tr>
               <td> Hire </td>
               <td> {hireInfo['name']} </td>
            </tr>
            <tr>
               <td> Start </td>
               <td> {hireInfo['start_date']} </td>
            </tr>
            <tr>
               <td> Hire Status </td>
               <td> {hireInfo['hire_status']} </td>
            </tr>
            <tr>
               <td> Ticket(s) </td>
               <td> {hireInfo['tickets_found'] || 'none'} </td>
            </tr>
            <tr>
               <td> Computer Ordered </td>
               <td> {hireInfo['computer_model'] || 'none'} </td>
            </tr>
            <tr>
               <td> Computer Status </td>
               <td> {hireInfo['depot_status'] || 'not started'} </td>
            </tr>
         </tbody>
         </table>
      );
   };


   return (
      <div className='hire-details'>
         <h3> Hire Details </h3>
         <br/>
         {detailsTable()}

         <br/> <hr /> <br/>

         <h3> Action Items </h3>
         <br/>
         {actionItemsTable()}

         <br/> <hr /> <br/> 
         
         <h3> Further Info </h3>
         <br/>

         Reach out to {hireInfo['talent_coordinator']} (Talent Coordinator)
         for questions regarding hire status, or your respective Depot
         DL for computer questions:<br/>
         <br/>
         &nbsp; -&gt; <a href='mailto: sjdepot@adobe.com'> San Jose </a><br/>
         &nbsp; -&gt; <a href='mailto: sfdepot@adobe.com'> San Francisco </a><br/>
         &nbsp; -&gt; <a href='mailto: utdepot@adobe.com'> Lehi & Remote </a><br/>
      </div>
   );
};

export default HireDetails;
