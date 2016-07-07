#!/usr/bin/env python

"""
nba_from_players_first_two_injuries.py

Print player information and stats for players up to their first injury.

This script expects a plain-text config file saved to `~/.my.cnf` with at
least: `user`, `password`, `host`, `database` defined under the `client` option
group. For more info on mysql option files see:
http://dev.mysql.com/doc/refman/5.7/en/option-files.html
"""

from __future__ import print_function
import mysql.connector  # available on PyPi as `mysql-connector`
import os.path
from itertools import groupby

config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
connection = mysql.connector.connect(option_files=config_file)

players_all_injuries = connection.cursor(named_tuple=True, buffered=True)
query = """SELECT abbr, first, last, age, birthdate, date, injury_type, main_body_part, specific_body_part
             FROM test_nbaGameInjuries
            WHERE g_missed != 0"""
players_all_injuries.execute(query)

# NOTE: assumes `abbr` is unique
# get the first two injuries for each player
players_first_two_injuries_dates = {}
for key, player in groupby(players_all_injuries, lambda x: x[0]):
    p = list(player)
    if len(p) > 1:
        players_first_two_injuries_dates[key] = p[:2]

query = """SELECT first, last, age, ht, wt, pos, COUNT(date) as gp, SUM(mp) as mp
             FROM test_nbaGameInjuries
            WHERE (censor = 'RIGHT' OR censor = 'NONE') AND first = %s AND last = %s AND birthdate = %s AND date > DATE(%s) AND date <= DATE(%s)"""
print("first, last, age, ht, wt, pos, gp, mp, first: injury_type, main_body_part, specific_body_part, second: injury_type, main_body_part, specific_body_part")
cursor = connection.cursor(prepared=True)
for abbr, player in players_first_two_injuries_dates.items():
    cursor.execute(query, (player[0].first, player[0].last,
                           player[0].birthdate, player[0].date, player[1].date,))
    players_first_two_injuries = cursor.fetchall()
    for (first, last, age, ht, wt, pos, gp, mp) in players_first_two_injuries:
        if first:
            print(first.decode("utf-8"), last.decode("utf-8"),
                  age.decode("utf-8"), ht, wt, pos.decode("utf-8"), gp,
                  mp.decode("utf-8") if mp else 0, sep = ", ", end = ", ")
            print("first: {}, {}, {}, second: {}, {}, {}".format(player[0].injury_type,
                                                                 player[0].main_body_part,
                                                                 player[0].specific_body_part,
                                                                 player[1].injury_type,
                                                                 player[1].main_body_part,
                                                                 player[1].specific_body_part))

connection.close()
