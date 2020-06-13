#!/usr/bin/env python3
# admin.py
# Tool to manage user accounts
#
# Add / remove accounts,
# Set / modify passwords,
# Authorization, account defaults, etc.

import json
import scrypt
import sqlite3
from   getpass  import  getpass
from   pathlib  import  Path

# Kinda a messy way to do this, but it works
database = str(Path(__file__).resolve().parents[1] / 'data/database.db')

conn = sqlite3.connect(database)
c    = conn.cursor()

def header():
   print('\nUser Administration:\n')


def tasty_breakfast(potatoes, salt):
   ''' Encrypts password '''
   return scrypt.hash(potatoes, str(salt))


def verify_user_exists(user_id):
   ''' Retrns True if user exists in DB, else false '''
   c.execute('select count(*) from users where user_id = ?', [user_id])
   conn.commit()
   return c.fetchone()[0]


def add_user_prompt():
   ''' Prompts for user information to write to db '''
   print('\nAdd User\n')
   user_id = input('user ID\n> ')

   if verify_user_exists(user_id):
      print('ERROR--user_id already exists')
      return

   username = input('username\n> ')

   password = getpass('password\n> ')
   verify = getpass('password (confirm)\n> ')

   if password != verify:
      print('ERROR--passwords do not match')
      return

   password = tasty_breakfast(password, user_id)
   add_user(user_id, username, password)


def add_user(user_id:int, username, password, permissions=None, defaults=None):
   '''
   Adds user to the database.

   Requires: username, password
   Optional: permissions: list, defaults: dict

   Columns:
      user_id
      username
      password
      permissions
      defaults
   '''
   try:
      c.execute('insert into users values (?, ?, ?, null, null)', [user_id, username, password])
      conn.commit()
      print('\nAdded.\n')
   except Exception as e:
      print(f'ERROR--{e}')


def modify_user_prompt():
   '''
   Prompts for user_id, and operation to preform.
   Must pass user_id, column, and new_value to modify_user()
   '''
   print('\nModify User\n')
   user_id = input('user_id\n> ')

   if not verify_user_exists(user_id):
      print('ERROR--user not found')
      return

   action = input('\nWant to modify ...\n   (p)ass, or\n   (d)efaults\n> ') 

   #-----| change password |-----#
   if action == 'p':
      password = getpass('password\n> ')
      verify = getpass('password (confirm)\n> ')

      if password != verify:
         print('ERROR--passwords do not match')

      password = tasty_breakfast(password, user_id)
      modify_user(user_id, 'password', password)

   #-----| change defaults |-----#
   # Modifies website settings,
   # e.g., theme / view / landing page
   elif action == 'd':
      defaults = {'theme': 'ag-theme-balham',
                  'view': 'depot',
                  'landing': 'home'}

      theme = input('\ntheme (light|dark) default: light)?\n> ')
      if theme == 'light':
         defaults['theme'] = 'ag-theme-balham'
      elif theme == 'dark':
         defaults['theme'] = 'ag-theme-balham-dark'

      view = input('view (depot|onboarding|all) default: depot)\n> ')
      if view in ['depot', 'onboarding', 'all']:
         defaults['view'] = view

      landing = input('landing page (home|worksheet|managers) default: home)\n> ')
      if landing in ['home', 'worksheet', 'managers']:
         defaults['landing'] = landing

      # DEBUGGING
      #
      #try:
      #   json.loads(defaults)
      #except json.JSONDecodeError as e:
      #   print(f'Invalid JSON: {e}')
      #   raise SystemExit

      modify_user(user_id, 'defaults', json.dumps(defaults))


def modify_user(user_id, column, new_value):
   ''' Modifies permissions, defaults, or password '''
   assert column in ['password', 'permissions', 'defaults']
   try:
      c.execute(f'update users set {column} = ? where user_id = ?',
         [new_value, user_id])
      conn.commit()
      print('\nUpdated.\n')
   except Exception as e:
      print(f'ERROR--{e}')
      return


def delete_user_prompt():
   ''' Prompts for user_id, confirms user exists, confirms delete '''
   print('Delete User')
   user_id = input('user_id\n> ')

   if not verify_user_exists(user_id):
      print('ERROR--user not found')
      return

   confirm = input('confirm (y/n)\n> ')

   if confirm != 'y':
      print("Answer not 'y', aborting.")
      return

   delete_user(user_id)


def delete_user(user_id):
   ''' Deletes user from DB '''
   try:
      c.execute('delete from users where user_id = ?', [user_id])
      conn.commit()
   except Exception as e:
      print(f'ERROR--{e}')
      return


def operation_to_perform():
   print('What action to take?')
   print('   (a)dd')
   print('   (m)odify')
   print('   (d)elete')

   while True:
      res = input('> ')
      if res not in ['a', 'm', 'd']:
         print('invalid response')
         continue
      else:
         break
   return res


def main():
   header()
   operation = operation_to_perform()
   if operation == 'a':
      add_user_prompt()
   elif operation == 'm':
      modify_user_prompt()
   elif operation == 'd':
      delete_user_prompt()
   conn.close()

if __name__ == '__main__':
   main()
