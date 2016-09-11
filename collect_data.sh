#!/usr/bin/env bash

set -e

#mysql -Be "CALL nbaGetNeverInjured();" | tr '\t' ',' | sed 's/NULL//g' > nba_never_injured.csv
#python3 nba_upto_first_injury.py
# python3 nba_from_first_to_second_injury.py > nba_from_first_to_second_injury.txt

python nba_never_injured.py
python nba_upto_first_injury.py
python nba_upto_first_and_only_injury.py
python nba_from_first_to_second_injury.py
