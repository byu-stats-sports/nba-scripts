"""
nba_never_injured.py

This script will perform a left join (all players - players who have been injured)
to determine the NBA players who have never been injured.

Notes:
    If you get errors like: "... incompatible with sql_mode=only_full_group_by"
    see: http://stackoverflow.com/questions/23921117/disable-only-full-group-by

This script expects a plain-text config file saved to `~/.my.cnf` with at
least: `user`, `password`, `host`, `database` defined under the `client` option
group. For more info on mysql option files see:
http://dev.mysql.com/doc/refman/5.7/en/option-files.html

Usage:
    python nba_never_injured.py OR python3 nba_never_injured.py
 """

from __future__ import print_function
from pprint import pprint
import csv
import mysql.connector  # available on PyPi as `mysql-connector`
import os
import sys


config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
connection = mysql.connector.connect(option_files=config_file)

cursor = connection.cursor(dictionary=True)
players = cursor.callproc('nbaGetNeverInjuredPlayers')
cursor.close()
connection.close()

pprint(players)

# name the output file after this script's filename
filename = os.path.splitext(sys.argv[0])[0]
with open('{}.csv'.format(filename),'w') as f:
    writer = csv.DictWriter(f, fieldnames=sorted(players[0].keys()))
    writer.writeheader()
    writer.writerows(players)
