import sqlite3

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

   def __init__(self):
      self.db   = '../database.db'
      self.conn = sqlite3.connect(self.db)

   def __enter__(self):
      return self.conn.cursor()

   def __exit__(self, etype, evalue, traceback):
      self.conn.close()


#=====| query |=====#
# Now that class has been established, make a query...

#query = '''
#        SELECT
#           workday.employee_id,
#           workday.name,
#           group_concat(tickets.sctask)
#        FROM workday
#        LEFT JOIN tickets
#           ON tickets.name = workday.name
#        GROUP BY tickets.name
#        '''

query = '''
        SELECT
           workday.name,
           group_concat(tickets.sctask),
           tickets.computer_options,
           tickets.computer_model,
           tickets.computer_status
        FROM workday
        LEFT JOIN tickets
           ON workday.name = tickets.name
        GROUP BY workday.name
        '''

with SQL() as c:
   print()
   for i in c.execute(query).fetchall():
      print(i)
   print()
