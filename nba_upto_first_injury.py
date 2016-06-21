#!/usr/bin/env python

from __future__ import print_function
import mysql.connector
import os.path

connection = mysql.connector.connect(
    option_files=os.path.join(os.path.expanduser('~'), '.my.cnf'))

injured_players = connection.cursor(buffered=True)
query = """SELECT first, last, abbr, birthdate, date
             FROM nbaGameInjuries
            WHERE g_missed != 0 
         GROUP BY abbr"""
injured_players.execute(query)

query = """SELECT first, last, pos, ht, wt, COUNT(abbr) as gp, SUM(mp) as mp, censor
             FROM nbaGameInjuries
            WHERE abbr = %s AND date < DATE(%s)"""
for (first, last, abbr, birthdate, date) in injured_players:
    upto_first_injury = connection.cursor(buffered=False)
    upto_first_injury.execute(query, (abbr, date,))
    for player in upto_first_injury:
        print(*player)
    upto_first_injury.close()

connection.close()
