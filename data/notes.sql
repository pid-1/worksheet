/*
-------------
 ALL COLUMNS
-------------
employee_id        --
name                 \
email                 |
start_date            |
hire_status           |
hired_date            |
worker_type           |
hire_type             |
manager               |
talent_coordinator    |
reminder_01           |--| Workday
reminder_02           |
reminder_03           |
requisition           |
ticket_req            |
extension             |
depot_status          |
onboarding_status     |
general_notes        /
version            --
sctask             --
req                  \
employee_id           |
name                  |
order_placed          |--| Tickets
requisition           |
computer_options      |
computer_model       /
computer_status    --
tickets_found      )-----| Created Columns

==========
  VIEWS
----------
 view_all
----------
(-) workday.ticket_req,
(-) tickets.req
(-) tickets.name
(-) tickets.order_placed,
(-) tickets.sctask
(-) tickets.requisition

-------------
 view_depot
-------------
employee_id
name
start_date
depot_status 
version
computer_options
computer_model
computer_status
tickets_found


=============
  OLD VIEWS
=============

CREATE VIEW IF NOT EXISTS view_all AS
SELECT
   workday.employee_id,
   workday.name,
   workday.email,
   workday.start_date,
   workday.hire_status,
   workday.hired_date,
   workday.worker_type,
   workday.hire_type,
   workday.manager,
   workday.talent_coordinator,
   workday.reminder_01,
   workday.reminder_02,
   workday.reminder_03,
   workday.requisition,
   workday.depot_status,
   workday.onboarding_status,
   workday.general_notes,
   workday.version,
   tickets.order_placed,
   tickets.computer_options,
   tickets.computer_model,
   tickets.computer_status,
   group_concat(tickets.sctask) AS tickets_found
FROM
   workday
LEFT JOIN
   tickets ON workday.employee_id = tickets.employee_id
WHERE
   worker_type LIKE '%Regular%' OR
   worker_type LIKE '%Agency%' OR
   worker_type LIKE '%Intern%'
GROUP BY
   workday.name
ORDER BY
   workday.start_date,
   tickets.order_placed;

CREATE VIEW IF NOT EXISTS view_depot AS
SELECT
   employee_id,
   name,
   start_date,
   depot_status, 
   version,
   computer_options,
   computer_model,
   computer_status,
   tickets_found
FROM
   view_all
WHERE
   hire_status = "5 - hired"
ORDER BY
   start_date,
   order_placed;

CREATE VIEW IF NOT EXISTS view_onboarding AS
SELECT
   employee_id,
   name,
   start_date,
   hire_status,
   manager,
   talent_coordinator,
   onboarding_status,
   version,
   order_placed,
   tickets_found
FROM
   view_all
ORDER BY
   start_date,
   hire_status,
   order_placed;
*/
