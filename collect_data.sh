#!/usr/bin/env bash

set -e

#mysql -Be "CALL nbaGetNeverInjured();" | tr '\t' ',' | sed 's/NULL//g' > nba_never_injured.csv
#python3 nba_upto_first_injury.py
# python3 nba_from_first_to_second_injury.py > nba_from_first_to_second_injury.txt

datasets=("nba_never_injured" "nba_upto_first_injury" "nba_upto_first_and_only_injury" "nba_upto_second_injury")

for dataset in "${datasets[@]}"
do
	echo "$dataset.py > $dataset.csv"
	python "$dataset.py" > "$dataset.csv"
done
