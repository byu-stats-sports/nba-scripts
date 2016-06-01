#!/usr/bin/env python

from __future__ import print_function
from itertools import filterfalse
import logging
import mysql.connector
import pprint
import sys

class Nba:
    def __init__(self, logger):
        self.logger = logger
        self.pp = pprint.PrettyPrinter(indent=1)
        self.connection = self._connection()

    def __del__(self):
        if self.connection:
            self.connection.close()

    def non_injured_players(self):
        all_players = self.all_players()
        injured_players = self.injured_players()
        non_injured_players = filterfalse(lambda p: self._contains(p['abbr'], 
                                                    injured_players, 
                                                    'abbr'), 
                                                    all_players)
        self.logger.debug(self.pp.pformat(non_injured_players))
        return non_injured_players
    
    def all_players(self):
        all_players_stmt = """SELECT first, last, abbr, pos, ht, wt, censor 
                           FROM nbaGameInjuries 
                           GROUP BY abbr"""
        all_players = self._execute(all_players_stmt)
        self.logger.debug(self.pp.pformat(all_players))
        return all_players

    def injured_players(self):
        injured_players_stmt = """SELECT first, last, abbr, pos, ht, wt, censor 
                               FROM nbaGameInjuries 
                               WHERE g_missed != 0 
                               GROUP BY abbr"""
        injured_players = self._execute(injured_players_stmt)
        self.logger.debug(self.pp.pformat(injured_players))
        return injured_players

    def _connection(self):
        try: 
            connection = mysql.connector.connect(host='statsports.byu.edu',
                                                 user='pstowell',
                                                 password='sp0rtsPS',
                                                 database='testJazz')
            self.logger.info(connection.get_server_info())
            return connection
        except Exception as e:
            self.logger.exception(e) 

    def _execute(self, stmt, args=None):
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            self.logger.debug("%s\nargs: %s", stmt, args)
            cursor.execute(stmt, (args))
            if cursor.with_rows:
                return cursor.fetchall()
            # connection.commit()
        except mysql.connector.Error as e:
            self.logger.exception(e)
        finally:
            if cursor:
                cursor.close()

    def _contains(self, item, item_list, key):
        found = False
        for i in item_list: 
            if i[key] == item: 
                found = True
        return found


def main():
    logger = logging.getLogger('nba')
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        level = logging.DEBUG
    else:
        level = logging.ERROR
    logging.basicConfig(level=level,
                        format='%(levelname)s [line:%(lineno)s]  %(message)s')
    nba = Nba(logger)
    
    # print(yaml.dump(list(nba.non_injured_players()), default_flow_style=False))

    for player in nba.non_injured_players():
        print("{first} {last} {pos} {ht} {wt} {censor}".format(**player))


if __name__ == "__main__":
    main()
