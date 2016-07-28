"""
nba_update_agility.py

Update the player (per season) with sportvu data
"""


from __future__ import print_function
import datetime
import dateutil.parser  # available on PyPi as `python-dateutil`
import mysql.connector  # available on PyPi as `mysql-connector`
import nba_py.league
import nba_py.player
from nba_py.constants import CURRENT_SEASON
import os
import sys
from collections import namedtuple


def games_by_season(season=CURRENT_SEASON):
    games = nba_py.league.GameLog(season=season, player_or_team='T').overall()
    return set(map(lambda g: g['GAME_DATE'], games))


def cleanup_name(name):
    #return name.lower().replace("'","").replace(".","").replace("?", "")
    return name.lower().replace("'","").replace("?", "")


def split_and_cleanup_name(name):
    try:
        first, last = name.split(' ', 1)
    except:
        if name == 'Nene':
            first = 'nene'
            last = 'hilario'
            pass
    first = cleanup_name(first)
    last = cleanup_name(last)
    return (first, last)


if __name__ == "__main__":
    config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
    connection = mysql.connector.connect(option_files=config_file)

    seasons = sys.argv[1:]
    if len(seasons) == 0:
        seasons = [CURRENT_SEASON]

    print("Downloading data...")
    players = set()
    for season in seasons:
        for game_date in games_by_season(season):
            for player in nba_py.league.PlayerSpeedDistanceTracking(season=season,
                                                                    date_from=game_date,
                                                                    date_to=game_date).overall():
                # print(player['PLAYER_NAME'])
                first, last = split_and_cleanup_name(player['PLAYER_NAME'])
                p = (player['DIST_MILES'],
                     player['AVG_SPEED'],
                     first,
                     last,
                     player['TEAM_ABBREVIATION'],
                     game_date)
                print(*p)
                players.add(p)
    sys.exit()
    print("Updating database...")
    stmt = """ALTER TABLE test_nbaGameInjuries
                ADD dist_miles decimal(6,2),
                ADD avg_speed decimal(6,2)"""
    cursor = connection.cursor(prepared=True)
    try:
        cursor.execute(stmt)
    except mysql.connector.errors.ProgrammingError as e:
        if e.errno == mysql.connector.errorcode.ER_DUP_FIELDNAME:
            pass
        else:
            raise(e)

    # NOTE: this assumes first, last and date are enough to uniquely identify a player
    stmt = """UPDATE test_nbaGameInjuries
                 SET dist_miles = %s
                     avg_speed = %s
               WHERE first = %s
                 AND last = %s
                 AND team = %s
                 AND date = %s"""
    cursor.executemany(stmt, players)
    connection.commit()
    cursor.close()

    connection.close()
