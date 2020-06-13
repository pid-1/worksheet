import sqlite3

c = sqlite3.connect('database.db').cursor()

#group_concat(tickets.sctask) as associated_tickets

# SELECT
#    workday.name,
#    CASE
#       WHEN tickets.sctask IS NOT null THEN
#          group_concat(tickets.sctask)
#       ELSE
#          0
#    END 'all_tickets'
# FROM workday
#    LEFT JOIN tickets ON workday.name = tickets.name
# GROUP BY tickets.name
# ORDER BY all_tickets DESC

#  SELECT
#     workday.name,
#     group_concat(tickets.sctask)  as "associated_tickets",
#     count(tickets.sctask)         as "tickets_per_hire"
#  FROM
#     workday
#  LEFT JOIN
#     tickets ON workday.name = tickets.name
#  GROUP BY
#     tickets.name
#  ORDER BY
#     tickets.order_placed


class SQL():
   setup =    ['''
               CREATE TABLE IF NOT EXISTS workday
                  (
                     uid     INTEGER,
                     name    TEXT
                  )
               ''',
               '''
               CREATE TABLE IF NOT EXISTS tickets
                  (
                     sctask  TEXT,
                     name    TEXT
                  )
               ''',
               '''
               INSERT INTO workday
                  ( uid, name     )
               VALUES
                  ( 100, "Marcus"   ),
                  ( 101, "Ginny"    ),
                  ( 102, "Nicholas" ),
                  ( 103, "Aurelius" ),
                  ( 104, "Susan"    ),
                  ( 105, "Giuliano" )
               ''',
               '''
               INSERT INTO tickets
                  ( sctask, name     )
               VALUES
                  ( "tkt001", "Marcus"   ),
                  ( "tkt002", "Ginny"    ),
                  ( "tkt003", "Nicholas" ),
                  ( "tkt004", "Aurelius" ),
                  ( "tkt005", "Aurelius" )
               ''']
   teardown = ['''
               DROP TABLE workday
               ''',
               '''
               DROP TABLE tickets
               ''']

   def __init__(self):
      ''' Initializing database/vars. '''
      self.db   = 'test_database.db'
      self.conn = sqlite3.connect(self.db)

   def __enter__(self):
      ''' Entering the function. '''
      for n, cmd in enumerate(self.setup):
         self.conn.cursor().execute(cmd)

      return self.conn.cursor()

   def __exit__(self, etype, evalue, traceback):
      ''' Exit cleanup functions. '''
      for n, cmd in enumerate(self.teardown):
         self.conn.cursor().execute(cmd)
      self.conn.close()


#=====| query |=====#
# Now that class has been established, make a query...

query = '''
        SELECT
           workday.uid,
           workday.name,
           group_concat(tickets.sctask)
        FROM workday
        LEFT JOIN tickets
           ON tickets.name = workday.name
        GROUP BY tickets.name
        '''

with SQL() as c:
   print()
   for i in c.execute(query).fetchall():
      print(i)
   print()
