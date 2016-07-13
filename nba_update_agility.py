"""
nba_update_agility.py

Update the player (per season) with agility data from the draft combine
"""


from __future__ import print_function
import datetime
import dateutil.parser  # available on PyPi as `python-dateutil`
import mysql.connector  # available on PyPi as `mysql-connector`
import nba_py.league
import nba_py.player
import nba_py.draftcombine
from nba_py.constants import CURRENT_SEASON
import os
import sys
from collections import namedtuple


def cleanup_name(name):
    return name.lower().replace("'","").replace("?", "")


def split_season(season):
    # NOTE: assumes 4 digit years...
    if not '-' in season or not len(season) == 7:
        raise ValueError('Season must be of the form: {}'.format(CURRENT_SEASON))
    start_year = int(season.split('-')[0])
    end_year = start_year + 1
    return (start_year, end_year)


def determine_seasons(seasons):
    Season = namedtuple('Season', ['raw', 'start_year', 'end_year'])
    results = []
    for season in seasons:
        try:
            results.append(Season(season, *split_season(season)))
        except ValueError as e:
            sys.exit(e)
    if len(results) < 1:
        results = [Season(CURRENT_SEASON, *split_season(CURRENT_SEASON))]
    return results



if __name__ == "__main__":
    config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
    connection = mysql.connector.connect(option_files=config_file)

    # first season in the database
    # FIXME: run query to figure this out...

    seasons = determine_seasons(sys.argv[1:])

    query = """SELECT MIN(season) as season
                 FROM test_nbaGameInjuries"""
    # FIXME: does not work as prepared so we have to create two cursors?
    cursor = connection.cursor(named_tuple=True)
    cursor.execute(query)
    first_season_year = cursor.fetchone().season - 1
    cursor.close()

    print("Downloading data...")
    players = set()
    #print("censor\tfirst\tlast\tbirthdate\tcareer_start\tcareer_end\t")
    for season in seasons:
        for player in nba_py.draftcombine.DrillResults(season=season).overall():
            p = (player['BENCH_PRESS'],
                 player['LANE_AGILITY_TIME'],
                 player['MODIFIED_LANE_AGILITY_TIME'],
                 player['MAX_VERTICAL_LEAP'],
                 player['STANDING_VERTICAL_LEAP'],
                 player['THREE_QUARTER_SPRINT'],
                 cleanup_name(player['FIRST_NAME']),
                 cleanup_name(player['LAST_NAME']),
                 season.end_year,
                 player['POSITION'])
            #print(*p)
            players.add(p)

    print("Updating database...")
    stmt = """ALTER TABLE test_nbaGameInjuries
                      ADD bench_press TINYINT,
                      ADD lane_agility_time DECIMAL(6,2),
                      ADD modified_lane_agility_time DECIMAL(6,2),
                      ADD max_vertical_leap DECIMAL(6,2),
                      ADD standing_vertical_leap DECIMAL(6,2),
                      ADD three_quarter_sprint DECIMAL(6,2)"""
    cursor = connection.cursor(prepared=True)
    try:
        cursor.execute(stmt)
    except mysql.connector.errors.ProgrammingError as e:
        if e.errno == mysql.connector.errorcode.ER_DUP_FIELDNAME:
            pass
        else:
            raise(e)

    # NOTE: this assumes first, last and pos are enough to uniquely identify a player
    stmt = """UPDATE test_nbaGameInjuries
                 SET bench_press = %s,
                     lane_agility_time = %s,
                     modified_lane_agility_time = %s,
                     max_vertical_leap = %s,
                     standing_vertical_leap = %s,
                     three_quarter_sprint = %s
               WHERE first = %s AND last = %s AND season = %s AND pos = %s"""
    cursor.executemany(stmt, players)
    connection.commit()
    cursor.close()

    connection.close()
