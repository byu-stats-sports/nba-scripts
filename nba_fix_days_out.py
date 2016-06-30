from __future__ import print_function
import mysql.connector  # available on PyPi as `mysql-connector`
import os


def days_between(s, f):
    # +1 because last_day_of_injury counts as a day...
    return abs((f - s).days + 1)


config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
connection = mysql.connector.connect(option_files=config_file)

incorrect = connection.cursor(named_tuple=True, buffered=True)
stmt = """SELECT first, last, birthdate, date, last_day_of_injury, days_out 
            FROM nbaGameInjuries 
           WHERE injury_type != 'None'
           ORDER BY last"""
incorrect.execute(stmt)
players = []
for p in incorrect:
    days_out = days_between(p.date, p.last_day_of_injury)
    players.append((days_out, p.first, p.last, p.birthdate,
                    p.date, p.last_day_of_injury))
incorrect.close()

stmt = """UPDATE nbaGameInjuries
             SET days_out = %s
           WHERE first = %s AND last = %s AND birthdate = %s AND date = %s AND last_day_of_injury = %s"""
correct = connection.cursor(prepared=True)
correct.executemany(stmt, players)
connection.commit()
correct.close()

connection.close()
