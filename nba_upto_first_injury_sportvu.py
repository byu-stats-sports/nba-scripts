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
from decimal import Decimal
import mysql.connector  # available on PyPi as `mysql-connector`
import os
import sys


def safe_decode(val):
    try:
        val = val.decode("utf-8")
    except AttributeError:
        val = 0
    return Decimal(val)


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
            WHERE career_from_year >= '2013'
              AND dist_miles IS NOT NULL
              AND dist_miles_off IS NOT NULL
              AND dist_miles_def IS NOT NULL
              AND avg_speed IS NOT NULL
              AND avg_speed_off IS NOT NULL
              AND avg_speed_def IS NOT NULL
              AND g_missed != 0
         GROUP BY first,
                  last,
                  birthdate
         ORDER BY last"""
cursor.execute(query)
injured_players = cursor.fetchall()
cursor.close()

query = """SELECT COUNT(date) as gp,
                  SUM(mp) as mp,
                  AVG(dist_miles) as avg_dist_miles,
                  AVG(dist_miles_off) as avg_dist_miles_off,
                  AVG(dist_miles_def) as avg_dist_miles_def,
                  AVG(avg_speed) as avg_speed,
                  AVG(avg_speed_off) as avg_speed_off,
                  AVG(avg_speed_def) as avg_speed_def
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

    for (gp, mp, avg_dist_miles, avg_dist_miles_off, avg_dist_miles_def,
         avg_speed, avg_speed_off, avg_speed_def) in cursor.fetchall():
        player['mp'] = safe_decode(mp)
        player['gp'] = gp
        player['avg_dist_miles'] = safe_decode(avg_dist_miles)
        player['avg_dist_miles_off'] = safe_decode(avg_dist_miles_off)
        player['avg_dist_miles_def'] = safe_decode(avg_dist_miles_def)
        player['avg_speed'] = safe_decode(avg_speed)
        player['avg_speed_off'] = safe_decode(avg_speed_off)
        player['avg_speed_def'] = safe_decode(avg_speed_def)

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
