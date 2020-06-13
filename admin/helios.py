#!/usr/bin/env python3
# helios.py
# Will simulate the day-to-day API calls made by the server
#
# Planning
#  - Effectively serves as a wrapper to `ito.py`
#  - Instead of being run on a cron job, will have an
#    administrative mode that advances the 'day', and
#    loads that corresponding day's JSON file. This
#    simulates successive API calls
#
#+--------------------------------------
# Step by step, what does it need to do:
#
# Prompt to reset current day to Monday,
#     Restore database.db to initial state
# Basic TUI interface (non-diaglog, clears on each entry)
#     Prompts to advance to the next day, and show incremental
#     changes via beautiful tables
#
# On each day advance...
#
# 1)  json.load the corresponding day's JSON file, to simulate
#     the response of an API call
# 2)  start analyzing workday data, then tickets
# 3)  workday:
#     a) Check for updates to existing entries
#        i. Make updates, write changes to "automated changes" table
#     b) Add remaining entries to the database
#     c) Write log of added / updated workday entries
# 4)  tickets:
#     a) Check for changes on existing tickets
#        i) Ensure ticket is not in manual-changes db
#        ii) If not, write changes to tickets table
#     b) Search for matching user for non-existing tickets
#     c) Add non-existing tickets to the database w/ user info
#     d) Write log of added / modified tickets
# 5)  Print output of added/changed tickets & workday info to terminal

import os
import re
import json
import pandas
import sqlite3
import colorama

from pathlib         import Path
from textwrap        import dedent
from datetime        import date, timedelta
#from beautifultable  import BeautifulTable

from api_utils       import run_analysis, reset_to_monday

# More accurate way of defining the path
jasons_house = Path(__file__).resolve().parents[1] / 'data/json/'

#=====| UTILITIES |=====#
# All utilities, overall system utilities first,
# specific functional utils later

# EDIT
# Delete this garbage in the final edit
def d(text=False):
   '''For debugging.'''
   if text:
      print('\n', text)
   raise SystemExit

colorama.init(autoreset=True)
def colortext(color, text):
   '''Formats colored text for success/failure messages.'''

   assert color in ['red', 'green', 'bold', 'bold red', 'bold green']

   if color == 'red':
      return colorama.Fore.LIGHTRED_EX + text
   if color == 'green':
      return colorama.Fore.LIGHTGREEN_EX + text
   if color == 'bold':
      return colorama.Style.BRIGHT + text
   if color == 'bold red':
      return colorama.Style.BRIGHT + colorama.Fore.LIGHTRED_EX + text
   if color == 'bold green':
      return colorama.Style.BRIGHT + colorama.Fore.LIGHTGREEN_EX + text


def red(text):
   '''Shortcut to call "colortext(red, text)".'''
   return colortext('red', text)


def green(text):
   '''Shortcut to call "colortext(green, text)".'''
   return colortext('green', text)


def display_loop(TODAY):
   debug = False
   if debug == True:
      tickets, workday = load_data('thursday')
      run_analysis(tickets, workday)
      return

   while True:
      tickets, workday = load_data(TODAY)
      run_analysis(tickets, workday)

      os.system('clear')
      print(dedent(f'''
      helios.py
      ---------

      Today is {TODAY}

      Would you like to ...
         - (a)dvance day
         - (r)eset to monday
      '''))

      res = input('> ')
      if res not in ['a', 'r']:
         print('ERROR--invalid input.')
         input()
         raise SystemExit

      if res == 'a':
         try:
            TODAY = advance_day(TODAY)
         except IndexError:
            print('\nUp to date. No day to advance to.\n')
            raise SystemExit
      if res == 'r':
         TODAY = 'monday'
         reset_to_monday()


def advance_day(TODAY):
   days = ['monday', 'tuesday', 'wednesday', 'thursday']
   n = days.index(TODAY)
   return days[n+1]


def load_data(today):
   # In which 'today' is set to 'monday', 'tuesday', ...

   workday = None
   tickets = None

   for jason in jasons_house.iterdir():

      if today not in jason.name:
         continue

      # Creates dict of dicts
      # {11001: { ... }, 11002: { ... }, ... }
      if 'workday' in jason.name:
         with open(jason) as wd:
            _workday = json.load(wd)
            
            workday = {}
            for values in _workday.values():
               workday[values['employee_id']] = values 
             
      # Creates dict of dicts
      # {sctask001: { ... }, sctask002: { ... }, ... }
      elif 'tickets' in jason.name:
         with open(jason) as tk:
            _tickets = json.load(tk)
            
            tickets = {}
            for values in _tickets.values():
               tickets[values['sctask']] = values 

   return tickets, workday


if __name__ == '__main__':
   # DEBUG
   # Reset to Monday on every start
   reset_to_monday()

   TODAY = 'monday'
   display_loop(TODAY)
