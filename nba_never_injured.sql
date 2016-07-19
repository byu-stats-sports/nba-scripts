DROP PROCEDURE IF EXISTS `nbaGetNeverInjured`;

DELIMITER //
 
CREATE PROCEDURE `nbaGetNeverInjuredPlayers`()
	LANGUAGE SQL
	DETERMINISTIC
	SQL SECURITY INVOKER 
COMMENT 'Return information for all players who have never been injured'
BEGIN
	SELECT
					players.first, 
					players.last, 
					players.age, 
					players.ht, 
					players.wt, 
					players.pos, 
					players.gp, 
					players.mp, 
					players.lane_agility_time, 
					players.modified_lane_agility_time, 
					players.max_vertical_leap, 
					players.standing_vertical_leap, 
					players.three_quarter_sprint, 
					players.bench_press 
		FROM 
				 --  all players
				 (SELECT
								 	first,
									last,
									MAX(age) as age,
									pos,
									ht,
									wt,
									COUNT(birthdate) as gp,
									SUM(mp) as mp,
									birthdate,
									lane_agility_time,
									modified_lane_agility_time,
									max_vertical_leap,
									standing_vertical_leap,
									three_quarter_sprint,
									bench_press
				  FROM	test_nbaGameInjuries
				 WHERE	censor = 'RIGHT'
						OR	censor = 'NONE'
			GROUP BY
								first,
								last,
								birthdate) players
	--  all players - players who have been injured = players who have never been injured
	LEFT JOIN
						--  players who have been injured at least once
						(SELECT
										first,
										last,
										MAX(age) as age,
										pos,
										ht,
										wt,
										birthdate,
										lane_agility_time,
										modified_lane_agility_time,
										max_vertical_leap,
										standing_vertical_leap,
										three_quarter_sprint,
										bench_press
							FROM 	test_nbaGameInjuries
						 WHERE 	g_missed != 0
							 AND	(censor = 'RIGHT' OR censor = 'NONE')
					GROUP BY	first,
										last,
										birthdate) injured
				ON	players.first = injured.first
			 AND	players.last = injured.last
			 AND	players.birthdate = injured.birthdate
		 WHERE	injured.first IS NULL
			 AND	injured.last IS NULL
			 AND	injured.birthdate IS NULL
	GROUP BY	players.first,
						players.last,
						players.birthdate
	ORDER BY	players.last;
END//
