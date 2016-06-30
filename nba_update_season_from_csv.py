from __future__ import print_function
from datetime import date, datetime, timedelta
import csv
#import dateutil.parser  # available on PyPi as `python-dateutil`
import mysql.connector  # available on PyPi as `mysql-connector`
import os
import sys


def convert_to_date(date):
    return datetime.strptime(date, '%m/%d/%Y').date()


def days_between(start, finish):
    return abs((finish - start).days)


def injury_duration(start, finish):
    # +1 because last_day_of_injury counts as a day...
    return days_between(start, finish) + 1


def player_name(player):
    p_name = player.split()
    return (p_name[0].lower(), p_name[1].lower())


season_last_day = convert_to_date('04/13/2016')
csv_file = sys.argv[1]

injury_games = [] 
print("Parsing {}...".format(csv_file))
with open(csv_file, 'r') as f:
    d = csv.DictReader(f)
  
    for player in d:
        player['first'], player['last'] = player_name(player['player'])
       
        try:
            player['date'] = convert_to_date(player['date'])
            player['birthdate'] = convert_to_date(player['birthdate'])
            player['g_missed'] = int(player['g_missed'])
        except:
            # do not add them to the database
            continue

        try:
            player['last_day_of_injury'] = convert_to_date(player['last_day_of_injury'])
        except:
            player['last_day_of_injury'] = season_last_day
        player['days_out'] = injury_duration(player['date'], player['last_day_of_injury'])

        injury_games.append((player['g_missed'],
                             player['main_body_part'],
                             player['specific_body_part'],
                             player['injury_type'],
                             player['laterality'],
                             player['last_day_of_injury'],
                             player['days_out'],
                             player['first'],
                             player['last'],
                             player['birthdate'],
                             player['date']))

from pprint import pprint
pprint(injury_games, indent=2)
sys.exit()

print("Updating database...") 
config_file = os.path.join(os.path.expanduser('~'), '.my.cnf')
connection = mysql.connector.connect(option_files=config_file)
cursor = connection.cursor(dictionary=True, buffered=True)
stmt = """UPDATE nbaGameInjuries
             SET g_missed = %s, 
                 main_body_part = %s, 
                 specific_body_part = %s, 
                 injury_type = %s, 
                 laterality = %s, 
                 last_day_of_injury = %s, 
                 days_out = %s
                WHERE first = %s 
                  AND last = %s 
                  AND birthdate = %s 
                  AND date = %s"""
cursor.executemany(stmt, injury_games)
connection.commit()
cursor.close()
connection.close()
