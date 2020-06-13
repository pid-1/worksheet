import React, { useState, useEffect } from 'react';
import axios from 'axios';

import Table from './Table';

const Worksheet = ({ view, theme }) => {

   const [tickets, setTickets] = useState([]);

   useEffect(() => {
      axios.get('https://nho.aurelius.org/api/v1/worksheet', {params: {view: view}})
         .then(res => {
            setTickets(res.data);
         })
         .catch(err => {
            console.log('ERROR', err.response);
         });
   }, [view]);


   if (tickets.length === 0) {
      return (
         <div>
            <h3><br/> Loading ... </h3>
         </div>
      )
   } else {
      return (
         <Table tickets={tickets} theme={theme} />
      );
   }
}

export default Worksheet;
