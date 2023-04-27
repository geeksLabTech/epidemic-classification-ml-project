

# work-related distributions
total_employees = 47100
total_population = 11181595
teacher_number = 4817
# probability distribution of active persons with respect to the total population
# the first element represents the probability that they are active
active_man_in_total_population = [0.421, 0.579]
# probability distribution of active people of working age
# the first element represents the probability that are active
active_people_in_working_age = [0.663, 0.336]

# probability distribution of men and women of working age
# the first element represents the probability that they are male
working_age = [0.606, 0.394]

# distribution of the probability of being active if you are a woman
# the first element represents the probability that they are active
active_woman_in_working_age = [0.548, 0.452]

# distribution of the probability of being active if you are a man
# the first element represents the probability that they are active
active_man_in_working_age = [0.768, 0.232]

# probability distribution of assets by sex
# the first element represents the probability that they are male
active_by_sex = [0.607, 0.393]

# gender distribution of professors
prefessors_by_sex = [0.689, 0.310]

# Population distributions

# positions in the list represents the following ranges:
# < 5, 5-9, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39,40-44, 45-49, 50-54, 55-59,60-64,65>
distribution_by_age_groups = [x/total_population for x in [559705,
                                                           620358,
                                                           578617,
                                                           639797,
                                                           697891,
                                                           722594,
                                                           791652,
                                                           676522,
                                                           660379,
                                                           927867,
                                                           985180,
                                                           934753,
                                                           626848,
                                                           1759432]]

# probability distribution of being a woman or a man
# the first element represents the probability that they are male
distribution_of_woman_or_man = [0.486, 0.496]

# level of study, the first position represents elementary school or less, the second secondary school,
# the third high school and the last higher education.
enrollment_distribution = [x for x in [1952, 9995, 24713, 10440]]
total_enrollment = 47100
