/*
 * nba_upto_first_injury.sql.sql
 *
 * This script will perform a left join (all players - players who have been injured) 
 * to determine the NBA players who have never been injured. 
 *
 * For each such player it reports:
 *	{first} {last} {birthdate} {height} {weight} {position} {career games} {career minutes} {censor}
 *	
 * Note: 
 * 	if you get errors like: "... incompatible with sql_mode=only_full_group_by"
 * 	see: http://stackoverflow.com/questions/23921117/disable-only-full-group-by 
 *
 * Usage: 
 *	mysql -u <user> -h <host> -p <database> < nba_upto_first_injury.sql.sql
 */

SELECT players.first, players.last, players.birthdate, players.date as first_injury, players.ht, players.wt, players.pos, players.gp, players.mp, players.censor
  FROM
		(SELECT first, last, abbr, date, birthdate, pos, ht, wt, COUNT(abbr) as gp, SUM(mp) as mp, censor
			 FROM nbaGameInjuries 
			 GROUP BY first, last, birthdate) players 
	RIGHT JOIN
		(SELECT first, last, abbr, date, birthdate, pos, ht, wt, censor
			 FROM nbaGameInjuries 
			WHERE g_missed != 0 
		  GROUP BY first, last, birthdate
			ORDER BY date) injured
	 ON players.abbr = injured.abbr AND players.date < injured.date
WHERE players.abbr IS NOT NULL
ORDER BY players.last
LIMIT 10;
