"""
 * nba_never_injured.sql
 *
 * This script will perform a left join (all players - players who have been injured)
 * to determine the NBA players who have never been injured.
 *
 * For each such player it reports:
 *	{first} {last} {birthdate} {height} {weight} {position} {career games} {career minutes} {censor}
 *
 * Note:
 * 	if you get errors like: "... incompatible with sql_mode=only_full_group_by"
 * 	see: http://stackoverflow.com/questions/23921117/disable-only-full-group-by
 *
 * Usage:
 *	mysql -u <user> -h <host> -p <database> < nba_never_injured.sql
 """

from __future__ import print_function
import mysql.connector  # available on PyPi as `mysql-connector`
import os

config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
connection = mysql.connector.connect(option_files=config_file)

query = """SELECT players.first, players.last, players.age, players.ht, players.wt, players.pos, players.gp, players.mp
           FROM
                   --  all players
                   (SELECT first, last, abbr, age, birthdate, pos, ht, wt, COUNT(abbr) as gp, SUM(mp) as mp, censor
                       FROM test_nbaGameInjuries
                       WHERE censor = 'RIGHT' OR censor = 'NONE'
                       GROUP BY first, last, birthdate) players
               LEFT JOIN  --  all players - players who have been injured = players who have never been injured
                   --  players who have been injured at least once
                   (SELECT first, last, abbr, age, birthdate, pos, ht, wt, censor
                       FROM test_nbaGameInjuries
                       WHERE g_missed != 0 AND (censor = 'RIGHT' OR censor = 'NONE')
                   GROUP BY first, last, birthdate) injured
               ON players.abbr = injured.abbr
           WHERE injured.abbr IS NULL
           GROUP BY players.abbr
           ORDER BY players.last;"""
cursor = connection.cursor()
cursor.execute(query)

print(*cursor.column_names, sep=', ')
for p in cursor:
    print(*p, sep=', ')

cursor.close()
connection.close()
