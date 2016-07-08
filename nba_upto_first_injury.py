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

# TODO: these really should be one complicated query instead of two for speed...

injured_players = connection.cursor(named_tuple=True, buffered=True)
query = """SELECT first, last, age, ht, wt, pos,
                  injury_type, main_body_part, specific_body_part,
                  MIN(date) as date, birthdate
             FROM test_nbaGameInjuries
            WHERE (censor = 'RIGHT' OR censor = 'NONE') AND g_missed != 0
         GROUP BY first, last, birthdate
         ORDER BY last"""
injured_players.execute(query)

query = """SELECT COUNT(date) as gp, SUM(mp) as mp
             FROM test_nbaGameInjuries
            WHERE first = %s
              AND last = %s
              AND birthdate = %s
              AND date <= DATE(%s)"""
upto_first_injury_player = connection.cursor(prepared=True)
print("first, last, age, ht, wt, pos, gp, mp, injury_type, main_body_part, specific_body_part")
for player in injured_players:
    upto_first_injury_player.execute(query,
                   (player.first, player.last, player.birthdate, player.date,))

    for (gp, mp) in upto_first_injury_player.fetchall():
        if player.first and player.pos:
            # FIXME mp fails for 'chris' 'mccullough'
            print(player.first, player.last, player.age, player.ht, player.wt,
                  gp, mp.decode("utf-8") if mp else 0,
                  player.injury_type, player.main_body_part, player.specific_body_part,
                  sep=', ')

injured_players.close()
upto_first_injury_player.close()
connection.close()
