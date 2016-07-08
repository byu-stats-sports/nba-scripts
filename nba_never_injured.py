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
import dateutil.parser  # available on PyPi as `python-dateutil`
import mysql.connector  # available on PyPi as `mysql-connector`
import datetime
import os


config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
connection = mysql.connector.connect(option_files=config_file)

query = """SELECT players.first, players.last, players.age, players.ht, players.wt, players.pos, players.gp, players.mp
           FROM
                   --  all players
                   (SELECT first, last, MAX(age) as age, pos, ht, wt, COUNT(birthdate) as gp, SUM(mp) as mp, birthdate
                       FROM test_nbaGameInjuries
                       WHERE censor = 'RIGHT' OR censor = 'NONE'
                       GROUP BY first, last, birthdate) players
               LEFT JOIN  --  all players - players who have been injured = players who have never been injured
                   --  players who have been injured at least once
                   (SELECT first, last, MAX(age) as age, pos, ht, wt, birthdate
                       FROM test_nbaGameInjuries
                       WHERE g_missed != 0 AND (censor = 'RIGHT' OR censor = 'NONE')
                   GROUP BY first, last, birthdate) injured
               ON players.first = injured.first AND players.last = injured.last AND players.birthdate = injured.birthdate
           WHERE injured.first IS NULL AND injured.last IS NULL AND injured.birthdate IS NULL
        GROUP BY players.first, players.last, players.birthdate
           ORDER BY players.last;"""
cursor = connection.cursor(named_tuple=True)
cursor.execute(query)

today = datetime.date.today()

#print(*cursor.column_names, 'age', sep=', ')
print('first, last, age, ht, wt, pos, gp, mp')
for p in cursor:
    #age = age_on(p.birthdate, today)
    print(p.first, p.last, p.age, p.ht, p.wt, p.pos, p.gp, p.mp, sep=', ')

cursor.close()
connection.close()
