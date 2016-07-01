#!/usr/bin/env python

"""
nba_upto_first_injury.py

Print player information and stats for players up to their first injury.
    
This script expects a plain-text config file saved to `~/.my.cnf` with at
least: `user`, `password`, `host`, `database` defined under the `client` option
group. For more info on mysql option files see:
http://dev.mysql.com/doc/refman/5.7/en/option-files.html 
"""

from __future__ import print_function
import mysql.connector  # available on PyPi as `mysql-connector`
import os.path

config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
connection = mysql.connector.connect(option_files=config_file)

cursor = connection.cursor(buffered=True)
query = """SELECT first, last, age, birthdate, date, injury_type, main_body_part, specific_body_part
             FROM test_nbaGameInjuries
            WHERE g_missed != 0 
         GROUP BY first, last, birthdate"""
cursor.execute(query)
injured_players = cursor.fetchall()
cursor.close()

# NOTE: this is making the assumption that `abbr` is unique
query = """SELECT first, last, age, ht, wt, pos, COUNT(date) as gp, SUM(mp) as mp
             FROM test_nbaGameInjuries
            WHERE censor = 'NONE' AND first = %s AND last = %s AND birthdate = %s AND date <= DATE(%s)"""
print("first, last, age, ht, wt, pos, gp, mp, injury_type, main_body_part, specific_body_part")
cursor = connection.cursor(prepared=True)
for (first, last, age, birthdate, date, injury_type, main_body_part, specific_body_part) in injured_players:
    cursor.execute(query, (first, last, birthdate, date,))
    upto_first_injury = cursor.fetchall()
    for (first, last, age, ht, wt, pos, gp, mp) in upto_first_injury:
        if first:
            print(", ".join([first.decode("utf-8"),
                             last.decode("utf-8"),
                             age.decode("utf-8"),
                             str(ht),
                             str(wt),
                             pos.decode("utf-8"),
                             str(gp),
                             mp.decode("utf-8"),
                             injury_type,
                             main_body_part,
                             specific_body_part])) 
cursor.close()
connection.close()
