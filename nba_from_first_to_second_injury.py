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
query = """SELECT abbr, date, injury_type, main_body_part, specific_body_part
             FROM nbaGameInjuries
            WHERE g_missed != 0"""
players_all_injuries.execute(query)

# get the first two injuries for each player
players_first_two_injuries_dates = {}
for key, player in groupby(players_all_injuries, lambda x: x[0]):
    p = list(player)
    if len(p) > 1:
        players_first_two_injuries_dates[key] = p[:2]

# NOTE: this is making the assumption that `abbr` is unique
query = """SELECT first, last, ht, wt, pos, 
                  COUNT(abbr) as gp, SUM(mp) as mp, censor
             FROM nbaGameInjuries
            WHERE abbr = %s AND date BETWEEN DATE(%s) AND DATE(%s)"""
for abbr, player in players_first_two_injuries_dates.items():
    players_first_two_injuries = connection.cursor(named_tuple=True)
    players_first_two_injuries.execute(query, 
                                       (abbr, player[0].date, player[1].date,))
    for p in players_first_two_injuries:
        if p.first:
            print("{}, {}, {}, {}, {}, {}, {}, {}, first: {}, {}, {}, second: {}, {}, {}"
                  .format(*p,
                          player[0].injury_type, 
                          player[0].main_body_part, 
                          player[0].specific_body_part,
                          player[1].injury_type, 
                          player[1].main_body_part, 
                          player[1].specific_body_part))
    players_first_two_injuries.close()

players_all_injuries.close()
connection.close()
