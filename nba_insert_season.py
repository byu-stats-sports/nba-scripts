from __future__ import print_function
from pprint import pprint
import datetime
import dateutil.parser  # available on PyPi as `python-dateutil`
import mysql.connector  # available on PyPi as `mysql-connector`
import nba_py.league
import nba_py.player
import os


# 201939 steph curry
# 201565 derrick rose

def convert_to_inches(height):
    try:
        h = height.split('-')
        feet = int(h[0])
        inches = int(h[1])
        ht = (feet * 12) + inches
    except:
        # sometimes height is Unknown or ''
        ht = None
    return ht


def search(player, players):
    return next(filter(
        lambda p: p['first'].lower() == player['FIRST_NAME'].lower() and 
                  p['last'].lower() == player['LAST_NAME'].lower() and 
                  p['birthdate'] == player['BIRTHDATE'], 
                  players))


def age_on(birthdate, date):
    d = dateutil.relativedelta.relativedelta(date, birthdate)
    age = d.years + d.months / 12 + d.days / 365.24
    return float("{:.2f}".format(age))


if __name__ == "__main__":
    # FIXME: dont need both 
    season = '2015-16'
    season_year = datetime.date(2016, 1, 1).year

    positions_map = {
        'Guard-Forward': 'SG',
        'Center-Forward': 'C',
        'Forward-Guard': 'SF',
        'Forward': 'SF',
        'Forward-Center': 'PF',
        'Guard': 'PG',
        'Center': 'C',
        '': None
    }
        
    config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
    connection = mysql.connector.connect(option_files=config_file)
    cursor = connection.cursor(dictionary=True, buffered=True)

    query = """SELECT first, last, birthdate, ht, wt, pos, censor
            FROM test_nbaGameInjuries
            GROUP BY first, last, birthdate"""
    cursor.execute(query)

    existing_players = cursor.fetchall()

    print("Downloading data...")
    new_players = []
    for player in nba_py.player.PlayerList(season=season).info():

        info = nba_py.player.PlayerSummary(player['PERSON_ID']).info()[0]
        info['BIRTHDATE'] = dateutil.parser.parse(info['BIRTHDATE']).date()
        info['HEIGHT'] = convert_to_inches(info['HEIGHT']) 
        try:
            info['WEIGHT'] = int(info['WEIGHT'])
        except:
            info['WEIGHT'] = None
        info['POSITION'] = positions_map[info['POSITION']]

        try:
            info['CENSOR'] = search(info, existing_players)['censor']
        except:
            # assume that rookies (players not in the db) will keep playing
            # after this season and are thus right censored
            info['CENSOR'] = 'RIGHT'
       
        for game in nba_py.player.PlayerGameLogs(player['PERSON_ID'],
                                                 season=season).info():
            date = dateutil.parser.parse(game['GAME_DATE']).date()
            new_players.append((info['FIRST_NAME'].lower(),
                                info['LAST_NAME'].lower(),
                                season_year,
                                game['MATCHUP'].split()[0], #HACK
                                info['HEIGHT'],
                                info['WEIGHT'],
                                info['BIRTHDATE'],
                                info['POSITION'],
                                date,
                                game['MIN'],
                                age_on(info['BIRTHDATE'], date),
                                info['CENSOR']))
 
    print("Updating database...") 
    # FIXME: what is idno??
    stmt = """REPLACE INTO test_nbaGameInjuries
                          (idno, first, last, season, team, ht, wt, birthdate,
                           pos, date, mp, age, censor)
                   VALUES (0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.executemany(stmt, new_players)
    connection.commit()
    cursor.close()
    connection.close()
