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
from pprint import pprint
import csv
import mysql.connector  # available on PyPi as `mysql-connector`
import os
import sys


config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
connection = mysql.connector.connect(option_files=config_file)

# TODO: these really should be one complicated query instead of two for speed...

cursor = connection.cursor(dictionary=True, buffered=True)
query = """SELECT first,
                  last,
                  age,
                  ht,
                  wt,
                  pos,
                  MIN(date) as date,
                  birthdate,
                  lane_agility_time,
                  modified_lane_agility_time,
                  max_vertical_leap,
                  standing_vertical_leap,
                  three_quarter_sprint,
                  bench_press
             FROM test_nbaGameInjuries
            WHERE (censor = 'RIGHT' OR censor = 'NONE')
              AND g_missed != 0
         GROUP BY first,
                  last,
                  birthdate
         ORDER BY last"""
cursor.execute(query)
injured_players = cursor.fetchall()
cursor.close()

query = """SELECT COUNT(date) as gp,
                  SUM(mp) as mp
             FROM test_nbaGameInjuries
            WHERE first = %s
              AND last = %s
              AND birthdate = %s
              AND date <= DATE(%s)"""
cursor = connection.cursor(prepared=True)

# Dr. Fellingham doesn't need these keys
blacklist_keys = ['date', 'birthdate']
for player in injured_players:
    cursor.execute(query, (player['first'], player['last'],
                           player['birthdate'], player['date'],))

    for (gp, mp) in cursor.fetchall():
        player['gp'] = gp
        try:
            mp = mp.decode("utf-8")
        except AttributeError:
            mp = 0
        player['mp'] = mp
    # remove blacklisted keys
    [player.pop(key) for key in blacklist_keys]
    # print out the player each time so we can see the data as we fetch it
    pprint(player)

cursor.close()
connection.close()

# name the output file after this script's filename
filename = os.path.splitext(sys.argv[0])[0]
# Dr. Fellingham wants these keys last as they don't match up with the keys
# from `nba_never_injured.py`...
#extra_keys = ['injury_type', 'main_body_part', 'specific_body_part']
#keys = [key for key in injured_players[0].keys() if key not in extra_keys]
with open('{}.csv'.format(filename),'w') as f:
    writer = csv.DictWriter(f, fieldnames=sorted(injured_players[0].keys()))
    writer.writeheader()
    writer.writerows(injured_players)
