"""nba_never_injured_sportvu.py

This script will perform a left join (all players - players who have been injured)
to determine the NBA players who have never been injured.

For each such player it reports:
    {first} {last} {birthdate} {height} {weight} {position} {career games} {career minutes} {censor}

Note:
    If you get errors like: "... incompatible with sql_mode=only_full_group_by"
    see: http://stackoverflow.com/questions/23921117/disable-only-full-group-by

    This script expects a plain-text config file saved to `~/.my.cnf` with at
    least: `user`, `password`, `host`, `database` defined under the `client` option
    group. For more info on mysql option files see:
    http://dev.mysql.com/doc/refman/5.7/en/option-files.html

Usage:
    python nba_never_injured.py
"""

from __future__ import print_function
from pprint import pprint
import csv
import mysql.connector  # available on PyPi as `mysql-connector`
import os
import sys


config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
connection = mysql.connector.connect(option_files=config_file)

query = """SELECT players.first,
                  players.last,
                  players.age,
                  players.ht,
                  players.wt,
                  players.pos,
                  players.gp,
                  players.mp,
                  players.lane_agility_time,
                  players.modified_lane_agility_time,
                  players.max_vertical_leap,
                  players.standing_vertical_leap,
                  players.three_quarter_sprint,
                  players.avg_dist_miles,
                  players.avg_dist_miles_off,
                  players.avg_dist_miles_def,
                  players.avg_speed,
                  players.avg_speed_off,
                  players.avg_speed_def
            FROM
                   --  all players
                   (SELECT first,
                           last,
                           MAX(age) as age,
                           pos,
                           ht,
                           wt,
                           COUNT(birthdate) as gp,
                           SUM(mp) as mp,
                           birthdate,
                           lane_agility_time,
                           modified_lane_agility_time,
                           max_vertical_leap,
                           standing_vertical_leap,
                           three_quarter_sprint,
                           bench_press,
                           AVG(dist_miles) as avg_dist_miles,
                           AVG(dist_miles_off) as avg_dist_miles_off,
                           AVG(dist_miles_def) as avg_dist_miles_def,
                           AVG(avg_speed) as avg_speed,
                           AVG(avg_speed_off) as avg_speed_off,
                           AVG(avg_speed_def) as avg_speed_def
                      FROM test_nbaGameInjuries
                     WHERE career_from_year >= '2013'
                  GROUP BY first,
                           last,
                           birthdate) players
       --  all players - players who have been injured = players who have never been injured
       LEFT JOIN
                   --  players who have been injured at least once
                   (SELECT first,
                           last,
                           birthdate
                      FROM test_nbaGameInjuries
                     WHERE g_missed != 0
                       AND career_from_year >= '2013'
                  GROUP BY first,
                           last,
                           birthdate) injured
              ON players.first = injured.first
             AND players.last = injured.last
             AND players.birthdate = injured.birthdate
           WHERE injured.first IS NULL
             AND injured.last IS NULL
             AND injured.birthdate IS NULL
        GROUP BY players.first,
                 players.last,
                 players.birthdate
        ORDER BY players.last"""
cursor = connection.cursor(dictionary=True)
cursor.execute(query)
players = cursor.fetchall()
cursor.close()
connection.close()

pprint(players)

# name the output file after this script's filename
filename = os.path.splitext(sys.argv[0])[0]
with open('{}.csv'.format(filename),'w') as f:
    writer = csv.DictWriter(f, fieldnames=sorted(players[0].keys()))
    writer.writeheader()
    writer.writerows(players)
