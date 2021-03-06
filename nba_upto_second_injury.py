#!/usr/bin/env python

"""
nba_upto_second_injury.py

Print player information and stats upto a player's second injury for all
players who have been injured more than once. 

This script expects a plain-text config file saved to `~/.my.cnf` with at
least: `user`, `password`, `host`, `database` defined under the `client` option
group. For more info on mysql option files see:
http://dev.mysql.com/doc/refman/5.7/en/option-files.html
"""

from __future__ import print_function
from itertools import groupby
from operator import itemgetter
import csv
import mysql.connector  # available on PyPi as `mysql-connector`
import os.path
import sys


config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
connection = mysql.connector.connect(option_files=config_file)

players_all_injuries = connection.cursor(dictionary=True, buffered=True)
query = """SELECT first,
                  last,
                  date,
                  birthdate
             FROM test_nbaGameInjuries
            WHERE (censor = 'RIGHT' OR censor = 'NONE')
              AND ((injury_type IS NOT NULL AND injury_type != 'None') or g_missed > 0)"""
players_all_injuries.execute(query)

# get the first two injuries for each player
players_first_two_injuries_dates = {}
for key, player in groupby(players_all_injuries, itemgetter('first',
                                                            'last', 
                                                            'birthdate')):
    # sort by date just to be sure they are in the correct order...
    p = sorted(list(player), key=itemgetter('date')) 
    if len(p) > 1:
        players_first_two_injuries_dates[key] = p[:2]

players_all_injuries.close()

query = """SELECT first, 
                  last, 
                  MAX(age) as age, 
                  ht, 
                  wt, 
                  pos, 
                  COUNT(date) as gp, 
                  SUM(mp) as mp
             FROM test_nbaGameInjuries
            WHERE (censor = 'RIGHT' OR censor = 'NONE') 
              AND first = %s 
              AND last = %s 
              AND birthdate = %s 
              AND date <= DATE(%s)"""
cursor = connection.cursor(prepared=True)
injured_players = []
for key, player in players_first_two_injuries_dates.items():
    cursor.execute(query, (player[0]['first'], 
                           player[0]['last'],
                           player[0]['birthdate'], 
                           player[1]['date'],))
    players_first_two_injuries = cursor.fetchall()
    for (first, last, age, ht, wt, pos, gp, mp) in players_first_two_injuries:
        if first:
            injured_players.append({'first': first.decode('utf-8'), 
                                    'last': last.decode('utf-8'),
                                    'age': age.decode('utf-8'), 
                                    'ht': ht, 
                                    'wt': wt, 
                                    'pos': pos.decode('utf-8'), 
                                    'gp': gp,
                                    'mp': mp.decode('utf-8') if mp else 0})
cursor.close()
connection.close()

writer = csv.DictWriter(sys.stdout, fieldnames=sorted(injured_players[0].keys()))
writer.writeheader()
writer.writerows(sorted(injured_players, key=itemgetter('last')))
