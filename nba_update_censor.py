"""
nba_update_censor.py

Update the censor entry for all players up to `season`.
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
    return name.lower().replace("'","")


def determine_censor(from_year, to_year, first_season_year, current_season_year):
    """
    Determine a censor for a given player.

    Args:
        from_year (int): The year the player started playing in the NBA.
        to_year (int): The year the player ended playing in the NBA (or the
            current year if still playing).
        current_season_year (int): The current season year: i.e. for the
            2015-2016 season this would be 2016.

    Returns:
        string: The censor- one of 'BOTH', 'LEFT', 'RIGHT' or 'NONE'.
    """
    if from_year < first_season_year and to_year >= current_season_year:
        censor = 'BOTH'
    elif from_year < first_season_year and to_year < current_season_year:
        censor = 'LEFT'
    elif from_year >= first_season_year and to_year >= current_season_year:
        censor = 'RIGHT'
    elif from_year >= first_season_year and to_year < current_season_year:
        censor = 'NONE'
    return censor


def split_season(season):
    # NOTE: assumes 4 digit years...
    if not '-' in season or not len(season) == 7:
        raise ValueError('Season must be of the form: {}'.format(CURRENT_SEASON))
    start_year = int(season.split('-')[0])
    end_year = start_year + 1
    return (start_year, end_year)


if __name__ == "__main__":
    config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
    connection = mysql.connector.connect(option_files=config_file)

    # first season in the database
    # FIXME: run query to figure this out...

    Season = namedtuple('Season', ['raw', 'start_year', 'end_year'])
    try:
        s = sys.argv[1]
        season = Season(s, *split_season(s))
    except IndexError as e:
        season = Season(CURRENT_SEASON, *split_season(CURRENT_SEASON))
    except ValueError as e:
        sys.exit(e)

    query = """SELECT MIN(season) as season
                 FROM test_nbaGameInjuries"""
    # FIXME: does not work as prepared so we have to create two cursors?
    cursor = connection.cursor(named_tuple=True)
    cursor.execute(query)
    first_season_year = cursor.fetchone().season - 1
    cursor.close()

    print("Downloading data...")
    players = set()
    print("censor\tfirst\tlast\tbirthdate\tcareer_start\tcareer_end\t")
    for player in nba_py.player.PlayerList(season=season,
                                            only_current=0).info():
        info = nba_py.player.PlayerSummary(player['PERSON_ID']).info()[0]

        if not info['TO_YEAR'] or info['TO_YEAR'] < first_season_year:
            continue

        p = (determine_censor(info['FROM_YEAR'], info['TO_YEAR'],
                              first_season_year, season.end_year),
                              cleanup_name(info['FIRST_NAME']),
                              cleanup_name(info['LAST_NAME']),
                              dateutil.parser.parse(info['BIRTHDATE']).date())
        print(*p, info['FROM_YEAR'], info['TO_YEAR'], sep="\t")
        players.add(p)

    sys.exit()

    print("Updating database...")
    stmt = """UPDATE test_nbaGameInjuries
                 SET censor = %s
               WHERE first = %s AND last = %s AND birthdate = %s"""
    cursor = connection.cursor(prepared=True)
    cursor.executemany(stmt, players)
    connection.commit()
    cursor.close()

    connection.close()
