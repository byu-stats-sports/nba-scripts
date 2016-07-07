#!/usr/bin/env bash

set -e

exe() {
	echo -e "$1"
	eval "$1"
}

exe "python3 nba_never_injured.py > nba_never_injured.txt"
exe "python3 nba_upto_first_injury.py > nba_upto_first_injury.txt"
exe "python3 nba_from_first_to_second_injury.py > nba_from_first_to_second_injury.txt"

