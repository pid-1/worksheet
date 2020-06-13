'''
Utilities to analyze the output of API calls to ServiceNow / Workday.

Entry point:
   - run_analysis(workday: dict, tickets: dict)
   - all other functions are _hidden

Input:
   - json data of tickets/workday data
Output:
   - writes to log-file with incremental changes
   - writes automated changes to database.db table
'''

# Planning
# May need to rethink this whole approach
#
# It makes sense to have the result of the API call be translated into
# a {primary_key: {'key': 'val', ...}, ...} sort of dataset
#
# Though it may not be the right choice to do that with all the data
# For intermediate data, can leave as a list, or a normal dict.

import sqlite3
from pathlib      import Path
from subprocess   import Popen
from textwrap     import dedent

PROGDIR = Path(__file__).resolve()

logfile = str(PROGDIR.parent / 'ongoing_log.txt')
database = str(PROGDIR.parents[1] / 'data/database.db')
restore_database = str(PROGDIR.parents[1] / 'data/backup/00_monday_restore.db')


def d(e=None):
   if e is not None:
      print(f'\n#=====| debug |=====#\n\n{e}\n')
      raise SystemExit


class SQL:
   def __init__(self, json_result=True):
      self.conn = sqlite3.connect(database)
      if json_result:
         self.conn.row_factory = self.dict_factory

   def __enter__(self):
      return self.conn.cursor()

   def __exit__(self, etype, evalue, traceback):
      if etype:
         write_log(f'ERROR HAS OCCURED -- {evalue} || on line: {traceback.tb_lineno}\n')
      else:
         self.conn.commit()
      self.conn.close()

   def dict_factory(self, cur, row):
      jsoned = {}
      for n, tup in enumerate(cur.description):
         # `cur.description` returns a tuple,
         #  confusingly enough it is a 7-tuple:
         #     (key, None, None, None, None, None, None)
         # This apparently is to fit with some Python API
         key = tup[0]
         value = row[n]

         jsoned[key] = value

      return jsoned


# EDIT
# Can probably remove all of these in the final edit,
#  unless we want to keep in just as a tool in a demo
def write_log(data):
   with open(logfile, 'a+') as f:
      f.write(str(data))


def _extract_data(tickets: dict, workday: dict) -> list:
   # EDIT
   # As we are not using q-mark notation, it will become essential to
   #  verify someone isn't trying to sql-injection us.
   # Though this data is being pulled from our database, and
   #  hypothetically we shouldn't have any entries with SQL, as they're
   #  pulled from Workday / SNOW directly

   # Slightlty iffy syntax ...
   # It's gotta be a string, and surrounded by quotes
   #  or SQL will think it's a column
   id_tickets = ', '.join([ f'"{t}"' for t in tickets ])
   id_workday = ', '.join([ f'"{w}"' for w in workday ])

   sql_exists_tickets = f'''
         SELECT  *
         FROM    tickets
         WHERE   sctask IN ({id_tickets})
         '''
   sql_exists_workday = f'''
         SELECT  *
         FROM    workday
         WHERE   employee_id IN ({id_workday})
         '''
   
   with SQL() as c:
      exists_tickets = c.execute(sql_exists_tickets).fetchall()
      exists_workday = c.execute(sql_exists_workday).fetchall()

   # Vaguely convoluted ...
   # Creates a list of the tickets present in the API call,
   #  but not in our database: new entries
   id_new_tickets = set(tickets) - set( t['sctask'] for t in exists_tickets )
   id_new_workday = set(workday) - set( h['employee_id'] for h in exists_workday )

   new_tickets = [ tickets[t] for t in id_new_tickets ]
   new_workday = [ workday[h] for h in id_new_workday ]

   # exists_tickets is the OLD tickets, fuuuuckkkk
   # This is where I need to change this
   return new_tickets, exists_tickets, new_workday, exists_workday


def _transform_data(exists_tickets, tickets, exists_workday, workday):
   '''
   Effectively does the work of the old ito.py.
   Transforms / diffs the current data from new API call'd data.
   '''

   def diff(old_row: dict, new_row: dict) -> list:
      '''
      Compares the old row to the new one. Returns a list of lists.
      
      formats:
         old_row = {sctask: "sctask001", name: "...", ...}
         new_row = {sctask: "sctask001", name: "...", ...}

        returns
         changes = [[column, old_value, new_value], [...], ...]
      '''

      changes = []

      for key, old_value in old_row.items():
         # To catch all the occurances of 'None', 'null', & ''
         if not old_value and not new_row[key]:
            continue

         new_value = new_row[key]

         if str(old_value) != str(new_value):
            changes.append([key, old_value, new_value])

      return changes

   
   def manually_updated(key):
      '''Ensures the row has NOT been manually updated.
      All automatic updates are run by 'SYSTEM' rather than a UID
      
      Thank God I create the usernames, 'cause naming yourself
      'SYSTEM' is exactly something that Nicholas would do.'''

      # For each changes in the list of changes, validates
      #  that this change was not present in a manual update
      #
      # Process:
      #  1. select from updates where id matches
      #  2. for each entry in 'updates' column ...
      #        a) Check the column against the auto-update
      #        b) If column matches, `continue`

      # EDIT
      # Right now this just checks to see if there's ANY
      #  entry that was updated by not the system.
      # In the future should make sure it's more descriminating.
      # Check to see if the particular column that's being
      #  targetted wasn't previously updated.

      with SQL() as c:
         res = c.execute(f'''
            SELECT    changes
            FROM      updates
            WHERE      key = ?
              AND     updated_by IS NOT "SYSTEM"
            ORDER BY  date DESC
            ''', [key]).fetchone()

      return res


   ticket_changes = {}
   for old_ticket in exists_tickets:
      sctask = old_ticket['sctask']
      new_ticket = tickets[sctask]

      t_changes = diff(old_ticket, new_ticket)

      # If the record has already been manually updated, skip
      if manually_updated(sctask):
         continue

      if t_changes:
         ticket_changes[sctask] = t_changes
         #write_log(f'Updated ticket: '
         #           + str(sctask) + ' '
         #           + str(t_changes)
         #           + '\n')

   workday_changes = {}
   for old_hire in exists_workday:
      employee_id = old_hire['employee_id']
      new_hire = workday[employee_id]

      w_changes = diff(old_hire, new_hire)

      # If the record has already been manually updated, skip
      if manually_updated(employee_id):
         continue

      if w_changes:
         workday_changes[employee_id] = w_changes
         #write_log(f'Updated hire: '
         #           + str(employee_id) + ' '
         #           + str(w_changes)
         #           + '\n')

   return ticket_changes, workday_changes


def _add_new_entries(new_tickets, new_workday):
   '''Adds new entires to the database.'''

   with SQL() as c:
      #-----| tickets |-----#
      # Create SQL query to insert tickets
      if new_tickets:
         tickets_keys = ', '.join(new_tickets[0].keys())

         for ticket in new_tickets:

            ticket_values = [t for t in ticket.values()]

            # More dynamic way of doing the q-mark notation
            # Allows for easier expansion into the future
            qmarks = '?,' * len(ticket_values)
            qmarks = qmarks.rstrip(',')

            c.execute(f'''
                  INSERT INTO tickets  ({tickets_keys})
                  VALUES               ({qmarks})
                  ''', ticket_values)

      #-----| workday |-----#
      # Create SQL query to insert workday
      if new_workday:
         workday_keys = ', '.join(new_workday[0].keys())

         for hire in new_workday:
            hire_values = [h for h in hire.values()]

            # More dynamic way of doing the q-mark notation
            # Allows for easier expansion into the future
            qmarks = '?,' * len(hire_values)
            qmarks = qmarks.rstrip(',')

            c.execute(f'''
                  INSERT INTO workday  ({workday_keys})
                  VALUES               ({qmarks})
                  ''', hire_values)


def _load_data(ticket_changes, workday_changes):
   '''
   Uploads the transformed data back into the database
   '''

   # This section is also potentially susceptible to SQL injection
   #
   # Though shouldn't be too likely as all this data is being
   #  pulled from the database. Would have to already have SQL
   #  nonsense in the DB in the first place
   #
   # Plus... it doesn't really expose any sensitive data. That's
   #  sorta the whole point of this project.

   with SQL() as c:
      #-----| ticket changes |-----#
      if ticket_changes:
         for sctask, ticket_info in ticket_changes.items():

            sql_ticket_changes = []
            for ticket_change in ticket_info:
               t_col, t_old, t_new = ticket_change
               sql_ticket_changes.append(f'{t_col} = {t_new}')

            #-----| update ticket |-----#
            # EDIT
            # Should figure out a way of building this so it's
            #  not prone to SQL injection. I know this work:
            #  >>> sql = [('data', 'more_data'), ('data2', 'things')]
            #  >>> c.executemany('INSERT INTO table VALUES (?, ?)', sql)
            # Can probably build something off this concept.
            #
            # Builds query based on all the individual changes
            #  in the list of sql_ticket_changes
            sql_ticket_changes = ', '.join(sql_ticket_changes)
            c.execute(f'''
                  UPDATE  tickets
                  SET     {sql_ticket_changes}
                  WHERE   sctask = "{sctask}"
                  ''')

            #-----| track updates |-----#
            # Writes updated row to "updates" table:
            #  - key          sctask    OR  employee_id
            #  - updated_by   'SYSTEM'  OR  user_id
            #  - date         datetime('now', 'localtime')
            #  - changes      [[...], [...], ...]
            c.execute(f'''
                  INSERT INTO  updates
                  VALUES (
                               ?,
                               "SYSTEM",
                               datetime('now', 'localtime'),
                               ?
                         )
                  ''', [sctask, str(ticket_info)])


      #-----| workday changes |-----#
      if workday_changes:
         for employee_id, hire_info in workday_changes.items():

            sql_hire_changes = []
            for hire_change in hire_info:
               w_col, w_old, w_new = hire_change
               sql_hire_changes.append(f'{w_col} = "{w_new}"')

            #-----| update workday |-----#
            # Builds query based on all the individual changes
            #  in the list of sql_workday_changes
            sql_hire_changes = ', '.join(sql_hire_changes)
            c.execute(f'''
                  UPDATE  workday
                  SET     {sql_hire_changes}
                  WHERE   employee_id = "{employee_id}"
                  ''')

            #-----| track updates |-----#
            # See `33k` for docs
            c.execute(f'''
                  INSERT INTO  updates
                  VALUES (
                               ?,
                               "SYSTEM",
                               datetime('now', 'localtime'),
                               ?
                         )
                  ''', [employee_id, str(hire_info)])


def reset_to_monday():
   '''
   Just blasts the current database,
   copies the backup one overtop of it.
   '''
   restore = Popen(['cp', restore_database, database])
   out, err = restore.communicate(timeout=5)

   # EDIT
   # Instead of restoring to the default db, make '00_monday.db' an
   #  empty database.
   # The initial run will then add all the previously non-existent
   #  entries to the db.

   if err:
      write_log('\nERROR RESTORING DB -- {err}\n')
      raise SystemExit


def run_analysis(tickets, workday):
   '''
   Effectively the `main()` function for api_utils

   Kicks off the sub-modules to analyze ticket data,
   and workday data.
   '''

   # EDIT
   # Need to go through and rename a lot of variables
   # It is clearly not a good idea to call them "exists_tickets"
   #  as they are more aptly described as the tickets which have
   #  PREVIOUSLY existed in the database (i.e., "old").
   # Whilst new_tickets are those which did *not* exist in the DB

   (new_tickets, exists_tickets,
    new_workday, exists_workday) = _extract_data(tickets, workday)

   ticket_changes, workday_changes = _transform_data(exists_tickets, tickets,
                                                   exists_workday, workday)
   _load_data(ticket_changes, workday_changes)
   _add_new_entries(new_tickets, new_workday)
