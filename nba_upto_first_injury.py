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

injured_players = connection.cursor(buffered=True)
query = """SELECT abbr, date, injury_type, main_body_part, specific_body_part
             FROM nbaGameInjuries
            WHERE g_missed != 0 
         GROUP BY abbr"""
injured_players.execute(query)

# NOTE: this is making the assumption that `abbr` is unique
query = """SELECT first, last, ht, wt, pos, 
                  COUNT(abbr) as gp, SUM(mp) as mp, censor
             FROM nbaGameInjuries
            WHERE abbr = %s AND date <= DATE(%s)"""
print("first, last, ht, wt, pos, gp, mp, censor, injury_type, main_body_part, specific_body_part")
for (abbr, date, injury_type, main_body_part, specific_body_part) in injured_players:
    upto_first_injury = connection.cursor(named_tuple=True, buffered=True)
    upto_first_injury.execute(query, (abbr, date,))
    for player in upto_first_injury:
        if player.first:
            print("{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}"
                  .format(*player,
                          injury_type, main_body_part, specific_body_part))
    upto_first_injury.close()

connection.close()
