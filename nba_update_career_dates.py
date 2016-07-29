"""
nba_update_career_dates.py

Update the career_from_year and career_to_year
"""

from __future__ import print_function
import datetime
import dateutil.parser  # available on PyPi as `python-dateutil`
import mysql.connector  # available on PyPi as `mysql-connector` import nba_py.league
import nba_py.player
from nba_py.constants import CURRENT_SEASON
import os
import sys
from collections import namedtuple


def cleanup_name(name):
    return name.lower().replace("'","").replace("?", "")


if __name__ == "__main__":
    config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
    connection = mysql.connector.connect(option_files=config_file)

    seasons = sys.argv[1:]
    if len(seasons) == 0:
        seasons = [CURRENT_SEASON]

    stmt = """ALTER TABLE test_nbaGameInjuries
                ADD career_from_year YEAR(4),
                ADD career_to_year YEAR(4)"""
    cursor = connection.cursor(prepared=True)
    try:
        cursor.execute(stmt)
    except mysql.connector.errors.ProgrammingError as e:
        if e.errno == mysql.connector.errorcode.ER_DUP_FIELDNAME:
            pass
        else:
            raise(e)

    print("Downloading data...")
    for season in seasons:
        players = set()
        for player in nba_py.player.PlayerList(season=season,
                                               only_current=0).info():

            info = nba_py.player.PlayerSummary(player['PERSON_ID']).info()[0]

            p = (info['FROM_YEAR'],
                 info['TO_YEAR'],
                 cleanup_name(info['FIRST_NAME']),
                 cleanup_name(info['LAST_NAME']),
                 dateutil.parser.parse(info['BIRTHDATE']).date())
            players.add(p)

        print("Updating database...")
        # NOTE: this assumes first, last, team & date are enough to uniquely identify a player
        stmt = """UPDATE test_nbaGameInjuries
                    SET career_from_year = %s,
                        career_to_year = %s
                  WHERE first = %s
                    AND last = %s
                    AND birthdate = %s"""
        cursor.executemany(stmt, players)
        connection.commit()

    cursor.close()
    connection.close()
