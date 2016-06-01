#!/usr/bin/env python

from __future__ import print_function
import mysql.connector
import logging
import pprint
from itertools import filterfalse
#import yaml


def execute(stmt, args=None):
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        logger.debug("%s\nargs: %s", stmt, args)
        cursor.execute(stmt, (args))
        if cursor.with_rows:
            return cursor.fetchall()
        # connection.commit()
    except mysql.connector.Error as e:
        logger.exception(e)
    finally:
        if cursor:
            cursor.close()


def contains(item, item_list, key):
    found = False
    for i in item_list: 
        if i[key] == item: 
            found = True
    return found


def main():
    logger = logging.getLogger('sportsstats')
    logging.basicConfig(level=logging.ERROR, 
                        format='%(levelname)s [line:%(lineno)s]  %(message)s')
    
    try: 
        connection = mysql.connector.connect(host='statsports.byu.edu',
                                             user='pstowell',
                                             password='sp0rtsPS',
                                             database='testJazz')
        logger.info(connection.get_server_info())
    except Exception as e:
        logger.exception(e) 

    pp = pprint.PrettyPrinter(indent=1)
    all_players_stmt = """SELECT first, last, abbr, pos, ht, wt, censor 
                       FROM nbaGameInjuries 
                       GROUP BY abbr"""
    all_players = execute(all_players_stmt)
    logger.debug(pp.pformat(all_players))

    injured_players_stmt = """SELECT first, last, abbr, pos, ht, wt, censor 
                           FROM nbaGameInjuries 
                           WHERE g_missed != 0 
                           GROUP BY abbr"""
    injured_players = execute(injured_players_stmt)
    logger.debug(pp.pformat(injured_players))

    non_injured = filterfalse(lambda p: contains(p['abbr'], 
                                                 injured_players, 
                                                 'abbr'), 
                                                 all_players)

    # print(yaml.dump(list(non_injured), default_flow_style=False))

    for player in non_injured:
        print("{first} {last} {pos} {ht} {wt} {censor}".format(**player))

if __name__ == "__main__":
    main()