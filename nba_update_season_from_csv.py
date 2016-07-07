from __future__ import print_function
from datetime import date, datetime, timedelta
import csv
import dateutil.parser  # available on PyPi as `python-dateutil`
import mysql.connector  # available on PyPi as `mysql-connector`
import os
import sys

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


def convert_to_date(date):
    return datetime.strptime(date, '%m/%d/%Y').date()


def days_between(start, finish):
    return abs((finish - start).days)


def cleanup_name(name):
    return name.lower().replace("'","")


def injury_duration(start, finish):
    # +1 because last_day_of_injury counts as a day...
    return days_between(start, finish) + 1


def age_on(birthdate, date):
    d = dateutil.relativedelta.relativedelta(date, birthdate)
    age = d.years + d.months / 12 + d.days / 365.24
    return float("{:.2f}".format(age))


def search(player, players):
    return next(filter(
        lambda p: cleanup_name(p['first']) == cleanup_name(player['first']) and
                  cleanup_name(p['last']) == cleanup_name(player['last']) and
                  p['birthdate'] == player['birthdate'],
                  players))

season_last_day = convert_to_date('04/13/2016')

config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
connection = mysql.connector.connect(option_files=config_file)

cursor = connection.cursor(dictionary=True, buffered=True)

query = """SELECT first, last, birthdate, ht, wt, pos, censor
        FROM test_nbaGameInjuries
        GROUP BY first, last, birthdate"""
cursor.execute(query)
existing_players = cursor.fetchall()
cursor.close()

injury_games = []
csv_file = sys.argv[1]
print("Parsing {}...".format(csv_file))
with open(csv_file, 'r') as f:
    d = csv.DictReader(f)

    for player in d:
        player['first'] = cleanup_name(player['first'])
        player['last'] = cleanup_name(player['last'])

        try:
            player['date'] = convert_to_date(player['date'])
            player['birthdate'] = convert_to_date(player['birthdate'])
            player['g_missed'] = int(player['g_missed'])
        except:
            # do not add them to the database
            continue

        player['ht'] = convert_to_inches(player['ht'])
        player['age'] = age_on(player['birthdate'], player['date'])

        # FIXME
        try:
            player['last_day_of_injury'] = convert_to_date(player['last_day_of_injury'])
        except:
            player['last_day_of_injury'] = season_last_day
        player['days_out'] = injury_duration(player['date'], player['last_day_of_injury'])

        try:
            existing_player = search(info, existing_players)
            player['censor'] = existing_player['censor']
        except:
            # assume that rookies (players not in the db) will keep playing
            # after this season and are thus right censored
            player['censor'] = 'RIGHT'

        player['mp'] = None  # FIXME

        # mysql-connector can't handle dynamically generated dicts (unorded keys)
        injury_games.append((player['age'],
                             player['birthdate'],
                             player['censor'],
                             player['date'],
                             player['days_out'],
                             player['first'].lower(),
                             player['g_missed'],
                             player['ht'],
                             player['injury_type'],
                             player['last'].lower(),
                             player['last_day_of_injury'],
                             player['laterality'],
                             player['main_body_part'],
                             player['mp'],
                             player['pos'],
                             player['season'],
                             player['specific_body_part'],
                             player['team'],
                             player['wt']))

stmt = """REPLACE INTO test_nbaGameInjuries
                       (idno, age, birthdate, censor, date, days_out, first,
                        g_missed, ht, injury_type, last, last_day_of_injury,
                        laterality, main_body_part, mp, pos, season,
                        specific_body_part, team, wt)
                VALUES (0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s)"""

print("Updating database...")
cursor = connection.cursor(prepared=True)
foo = """REPLACE INTO test_nbaGameInjuries
                       (idno, age, birthdate, censor, date, days_out, first,
                        g_missed, ht, injury_type, last, last_day_of_injury,
                        laterality, main_body_part, mp, pos, season,
                        specific_body_part, team, wt)
                VALUES (0, %(age)s, %(birthdate)s, %(censor)s, %(date)s,
                        %(days_out)s, %(first)s, %(g_missed)s, %(ht)s, %(injury_type)s,
                        %(last)s, %(last_day_of_injury)s, %(laterality)s,
                        %(main_body_part)s, %(mp)s, %(pos)s, %(season)s,
                        %(specific_body_part)s, %(team)s, %(wt)s)"""
cursor.executemany(stmt, injury_games)
connection.commit()
cursor.close()
connection.close()
