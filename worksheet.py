# Python Flask HTML backend
# Serves to handle API requests from React

import re, ast, json, scrypt, sqlite3
from textwrap        import dedent
from pathlib         import Path
from flask           import Flask, request, jsonify, Response, send_file, render_template
from flask_login     import LoginManager, UserMixin, login_user, current_user, login_required
from flask_socketio  import SocketIO, send, emit

PROGDIR = Path(__file__).resolve().parent

database = str(PROGDIR  / 'data/database.db')
logfile = str(PROGDIR / 'data/logfile.txt')
documentation_file = str(PROGDIR / 'public/documentation.wiki')
envfile = PROGDIR.joinpath('.env')

app = Flask(__name__,
      static_folder='./public',
      template_folder='./static')

with envfile.open() as f:
   app.secret_key = f.read()

# Set up socket.io
socket = SocketIO()
socket.init_app(app)

# Set up login manager
login_manager = LoginManager()
login_manager.init_app(app)


# EDIT
# Remove on final edit
def d(title, message):
   from textwrap import dedent
   print(dedent(f'''
         {title}
         -----
         {message}
         '''))


class User(UserMixin):
   def __init__(self, user_id):
      self.id = user_id


@login_manager.user_loader
def user_loader(user_id):
   with SQL() as c:
      check = c.execute('''
            SELECT  COUNT(*)
            FROM    users
            WHERE   user_id=?
            ''', [user_id]).fetchone()

   if check.get('COUNT(*)') == 1:
      return User(user_id)
   else:
      return None


class SQL():
   def __init__(self, row_factory=None):
      self.conn = sqlite3.connect(database)
      self.conn.row_factory = self.dict_factory

   def __enter__(self):
      return self.conn.cursor()

   def __exit__(self, etype, evalue, traceback):
      if etype:
         write_log(f'{etype}, {evalue}\n')
      else:
         self.conn.commit()
      self.conn.close()

   def dict_factory(self, cur, row):
      jsoned = {}
      for n, tup in enumerate(cur.description):
         # `c.description` returns a tuple,
         #  confusingly enough it is a 7-tuple:
         #     (key, None, None, None, None, None, None)
         # This apparently is to fit with some Python API
         key = tup[0]
         value = row[n]

         jsoned[key] = value

      return jsoned


#=====| UTILITIES |=====#

def write_log(log):
   with open(logfile, 'a') as f:
      f.write(f'{log}\n')


#-----| scrypt |-----#
# Encrypt / decrypt utilities

# Encrypts password
def tasty_breakfast(potatoes, salt):
   return scrypt.hash(potatoes, str(salt))


# Checks password against known
def taste_test(known, test):
   return known == test


#-----| sqlite3 utils |-----#
# All utilities relating to sqlite3

def route_to_table(column):
   '''
   Returns the correct table to put the data in
   '''
   table = ''

   if column in [ 'depot_status', 'onboarding_status', 'general_notes' ]:
      table = 'workday'
   elif column == 'tickets_found':
      table = 'tickets'
   else:
      write_log(f'ERROR in `route_to_table({column})\n')
      return

   return table


def update_tickets(employee_id, old_value, new_value):
   '''
   In which "old_value" was the "tickets_found" cell.
   It can have multiple associated tickets found with each entry.

   Updates new associated user unto the "new_value" ticket.

   If the new ticket is not found, will clear the 'employee_id'
   field to prevent incorrect data getting "stuck" on the frontend.
   '''

   # DECISION TREE
   # -------------
   #
   # new: ''
   #  [X] old: ''     - no edit made, disregard
   #  [X] old: value  - un-assigning ticket from that user
   #                       VALUE = NULL
   #                       WHERE = old_value
   #                       FALLBACK = print(err)
   # new: valid
   #  [X] old: ''     - no fallback possible, update normally
   #                       VALUE = employee_id
   #                       WHERE = new_value
   #                       FALLBACK = print(err)
   #  [X] old: value  - update normally
   #                       VALUE = employee_id
   #                       WHERE = new_value
   #                       FALLBACK = set old_value[0] to NULL
   # new: invalid
   #  [X] old: ''     - no fallback possible, return
   #                       VALUE = employee_id
   #                       WHERE = new_value
   #                       FALLBACK = print(err)
   #  [X] old: value  - set UID on old_value to 'NULL'
   #                       VALUE = employee_id
   #                       WHERE = new_value (invalid)
   #                       FALLBACK = set old_value[0] to NULL

   sql_check_exists = '''
            SELECT COUNT(*) as "number_found"
            FROM   tickets
            WHERE  sctask = ?'''
   sql_normal_update = '''
            UPDATE tickets
            SET    employee_id = ?
            WHERE  sctask = ?
            '''
   sql_fallback_update = '''
            UPDATE tickets
            SET    employee_id = NULL
            WHERE  sctask = ?
            '''
   sql_verify = '''
            SELECT *
            FROM   view_all
            WHERE  employee_id = ?
            '''

   # Shouldn't ever need this, but leaving it here in case.
   # Should the SQL statement fail, updated_row will be undefined.
   updated_row = None

   with SQL() as c:
      #-----| check 1 |-----#
      # Ensure the updated ticket exists in the DB
      c.execute(sql_check_exists, [new_value])
      count = c.fetchone()['number_found']

      #-----| normal case |-----#
      # If a ticket is found:
      if count == 1:
         # Update employee_id assignment for the ticket
         c.execute(sql_normal_update, [employee_id, new_value])
      else:
         #-----| fallback to null |-----#
         # If no ticket is found, clear out the employee_id assignment
         if old_value:
            old_value = old_value.split(',')[0]
            c.execute(sql_fallback_update, [old_value])

      # After normal case or fallback transactions occur,
      # return the updated row
      updated_row = c.execute(sql_verify, [employee_id]).fetchone()

   return updated_row


def update_workday(employee_id, column, new_value):
   '''
   Updates new information into corresponding workday entry
   '''
   # Shouldn't ever need this, but leaving it here in case.
   # Should the SQL statement fail, updated_row will be undefined.
   updated_row = None

   sql_verify = '''
            SELECT *
            FROM   view_all
            WHERE  employee_id = ?
            '''

   with SQL() as c:
      c.execute(f'''
            UPDATE
               workday
            SET
               {column} = ?
            WHERE
               employee_id = ?
         ''', [new_value, employee_id])

      updated_row = c.execute(sql_verify, [employee_id]).fetchone()

   return updated_row


#=====| SOCKET ROUTES |=====#
# All socket event listeners

@socket.on('connect')
def socket_on_connect():
   pass

@socket.on('message')
def socket_on_message(msg):
   debug('Received message', msg)


#=====| APP ROUTES |=====#
# All API routes for the app

@app.route('/', methods=['GET'])
def flask_index():
   return render_template('index.html')


@app.route('/login', methods=['POST'])
def flask_login():
   response = request.get_json(force=True)

   query_user_id  = response['userid']
   query_password = response['password']

   if not (query_user_id and query_password):
      return Response(status=400, response='Missing user_id or password')

   with SQL() as c:
      u = c.execute('''
            SELECT  *
            FROM    users
            WHERE   user_id=?
            ''', [query_user_id]).fetchone()

   if not u:
      return Response(status=400, response='User not found')

   # Nesting these functions for the sake of brevity
   #   tasty_breakfast(password, salt)
   #   taste_test(known, test)
   if taste_test(tasty_breakfast(query_password, query_user_id), u['password']):
      user = User(query_user_id)
      login_user(user)

      # EDIT
      # For debugging
      print(f'\n   UID: {query_user_id}\n   PASS: {query_password}\n   DEFAULTS: {u["defaults"]}\n')

      return jsonify(u['defaults'])
   else:
      return Response(status=401)


@app.route('/api/v1/help', methods=['GET'])
def flask_help():
   print('Sending:', documentation_file)
   return send_file(documentation_file, as_attachment=True)


@app.route('/api/v1/updates', methods=['GET'])
@login_required
def flask_updates():
   with SQL() as c:
      result = c.execute(f'''
            SELECT  *
            FROM    updates
            LIMIT   15
            ''').fetchall()

   for index, li in enumerate(result):
      jason_hates_this   = li['changes']
      jason_mediums_this = ast.literal_eval(jason_hates_this)   # <-- This shit is the key
      jason_approved     = json.dumps(jason_mediums_this)       # it strips the \' from str
                                                                # and turns back to list
      result[index]['changes'] = jason_approved

   return jsonify(result)


@app.route('/api/v1/worksheet', methods=['GET', 'PATCH'])
@login_required
def flask_worksheet():
   #=====| GET |=====#
   if request.method == 'GET':

      view = request.args.get('view')
      assert view in ['all', 'depot', 'onboarding', 'managers'], f'view was {view}'

      if view == 'all':
         view = 'view_all'
      elif view == 'depot':
         view = 'view_depot'
      elif view == 'onboarding':
         view = 'view_onboarding'
      elif view == 'managers':
         # EDIT
         # Putting this here temporarily
         #  before making a formal SQL view
         with SQL() as c:
            result = c.execute('''
                  SELECT
                     name,
                     start_date,
                     depot_status,
                     hire_status,
                     computer_model,
                     talent_coordinator,
                     tickets_found
                  FROM
                     view_all
                  WHERE
                     requisition = ?
                  ''', [request.args.get('req')]).fetchone()
         return jsonify(result)


      #-----| make query |-----#
      try:
         with SQL() as c:
            result = c.execute(f'''
                  SELECT *
                  FROM {view}
                  ''').fetchall()
         return jsonify(result)
      #-----| error handling |-----#
      except Exception as e:
         print(f'\nERROR:\n{e}\n')
         return Response(status=400, response=str(e))

   #=====| PATCH |=====#
   if request.method == 'PATCH':
      args = request.get_json(force=True)

      column    = args['col']
      old_value = args['oldValue']
      new_value = args['newValue']
      full_row  = args['row']

      table = route_to_table(column)
      if table not in ['tickets', 'workday']:
         Response(status=400, response='001--table not found')

      status  = 200
      results = ''

      employee_id = full_row['employee_id']

      #-----| update to tickets table |-----#
      # Only when changing user assigned to ticket
      if table == 'tickets':
         results = update_tickets(employee_id, old_value, new_value)

      #-----| update to workday table |-----#
      # When changing anything that's not the employee_id
      # associated with a particular ticket
      elif table == 'workday':
         results = update_workday(employee_id, column, new_value)

      socket.emit('rowUpdate', results,
            json=True, namespace='/', broadcast=True)

      return Response(status=200)


if __name__ == '__main__':
   socket.run(app, debug=True, port=8000)
