"""
 * nba_never_injured.py
 *
 * This script will perform a left join (all players - players who have been injured)
 * to determine the NBA players who have never been injured.
 *
 * For each such player it reports:
 *	 {first} {last} {birthdate} {height} {weight} {position} {career games} {career minutes} {censor}
 *
 * Note:
 * 	 If you get errors like: "... incompatible with sql_mode=only_full_group_by"
 * 	 see: http://stackoverflow.com/questions/23921117/disable-only-full-group-by
 *
 *   This script expects a plain-text config file saved to `~/.my.cnf` with at
 *   least: `user`, `password`, `host`, `database` defined under the `client` option
 *   group. For more info on mysql option files see:
 *   http://dev.mysql.com/doc/refman/5.7/en/option-files.html
 *
 * Usage:
 *   python nba_never_injured.py
 """

from __future__ import print_function
import dateutil.parser  # available on PyPi as `python-dateutil`
import mysql.connector  # available on PyPi as `mysql-connector`
import datetime
import os


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
                  players.bench_press
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
                           bench_press
                      FROM test_nbaGameInjuries
                     WHERE censor = 'RIGHT'
                        OR censor = 'NONE'
                  GROUP BY first,
                           last,
                           birthdate) players
       --  all players - players who have been injured = players who have never been injured
       LEFT JOIN
                   --  players who have been injured at least once
                   (SELECT first,
                           last,
                           MAX(age) as age,
                           pos,
                           ht,
                           wt,
                           birthdate,
                           lane_agility_time,
                           modified_lane_agility_time,
                           max_vertical_leap,
                           standing_vertical_leap,
                           three_quarter_sprint,
                           bench_press
                      FROM test_nbaGameInjuries
                     WHERE g_missed != 0 AND (censor = 'RIGHT' OR censor = 'NONE')
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
cursor = connection.cursor()
cursor.execute(query)

today = datetime.date.today()

print(*cursor.column_names, sep=', ')
for player in cursor:
    s = list(map(lambda p: p or '', player))
    print(*s, sep=', ')

cursor.close()
connection.close()
