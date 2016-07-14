    UPDATE test_nbaGameInjuries
INNER JOIN nbaGameInjuries ON (test_nbaGameInjuries.first = nbaGameInjuries.first
													AND  test_nbaGameInjuries.last = nbaGameInjuries.last
													AND  test_nbaGameInjuries.birthdate = nbaGameInjuries.birthdate
													AND  test_nbaGameInjuries.date = nbaGameInjuries.date)
       SET test_nbaGameInjuries.age = nbaGameInjuries.age,
           test_nbaGameInjuries.g_missed = nbaGameInjuries.g_missed,
           test_nbaGameInjuries.days_out = nbaGameInjuries.days_out,
           test_nbaGameInjuries.main_body_part = nbaGameInjuries.main_body_part,
           test_nbaGameInjuries.specific_body_part = nbaGameInjuries.specific_body_part,
           test_nbaGameInjuries.laterality = nbaGameInjuries.laterality,
           test_nbaGameInjuries.injury_type = nbaGameInjuries.injury_type,
           test_nbaGameInjuries.last_day_of_injury = nbaGameInjuries.last_day_of_injury,
           test_nbaGameInjuries.mp = nbaGameInjuries.mp;
