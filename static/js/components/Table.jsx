import React, { useEffect } from 'react';
import { AgGridReact }                from 'ag-grid-react';
import axios                          from 'axios';
import io                             from 'socket.io-client';

import { orderedKeys, columnProps }   from './MakeOrder';

import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-balham.css';
import 'ag-grid-community/dist/styles/ag-theme-balham-dark.css';

let api;
let socket;

const Table = ({ tickets, theme }) => {

   useEffect(() => {
      socket = io('https://nho.aurelius.org');

      socket.on('connect', () => {
         socket.on('rowUpdate', res => {
            rowUpdate(res);
         });
      });

      return () => socket.close()
   }, []);


   const allColumns = (
      Object.keys(tickets[0])
   );


   const orderedHeadings = orderedKeys.filter(
      entry => allColumns.includes(entry)
   );


   let columnDefs = orderedHeadings.map(item => {
      return {
         field: item,
         sortable: true,
         resizable: true,
         headerName: columnProps[item]['headerName'],
         filter: columnProps[item]['filter'],
         editable: columnProps[item]['editable'],
         hide: columnProps[item]['hide']
      };
   });


   const editHandler = row => {
      if (row.colDef.editable !== true) {
         // When you update the grid via its gridApi, that still triggered
         // `onCellValueChanged`, despite it not being a MANUAL change.
         return;
      }

      if (row.oldValue !== row.newValue) {
         axios({
            method: 'patch',
            url: 'https://nho.aurelius.org/api/v1/worksheet',
            data: {
               row: row.data,
               col: row.colDef.field,
               oldValue: row.oldValue,
               newValue: row.newValue
            }
         })
            .then(res => {
               console.log('editHandler(res)', res);
            })
            .catch(err => {
               console.log('editHandler(err)', err)
            });
      }
   };


   const rowUpdate = data => {
      let employeeId = data['employee_id'];

      // Find corresponding row on the grid for the employee_id
      let rowId = tickets.findIndex(x => x['employee_id'] === employeeId);
      let rowNode = api.getRowNode(rowId);

      rowNode.setData(data);
   };


   const initalApi = params => {
      params.api.sizeColumnsToFit();
   };


   return (
      <div className={theme} style={{ height: '94vh', width: '100vw' }}>
         <AgGridReact
            columnDefs={columnDefs}
            rowData={tickets}
            onCellValueChanged={editHandler}
            stopEditingWhenGridLosesFocus={true}
            onGridReady={e => {api = e.api}}
            onFirstDataRendered={initalApi}
            suppressChangeDetection={false}
         >
         </AgGridReact>
      </div>
   );
 
};

export default Table;
