

#work-related distributions
total_employees = 47100
total_population = 11181595
teacher_number = 4817
# probability distribution of active persons with respect to the total population
active_man_in_total_population = [0.421,0.579] # the first element represents the probability that they are active
# probability distribution of active people of working age
active_people_in_working_age = [0.663,0.336] #  the first element represents the probability that are active

# probability distribution of men and women of working age
working_age = [0.606, 0.394] # the first element represents the probability that they are male 

# distribution of the probability of being active if you are a woman
active_woman_in_working_age = [0.548, 0.452] # the first element represents the probability that they are active

# distribution of the probability of being active if you are a man
active_man_in_working_age = [0.768, 0.232] # the first element represents the probability that they are active

# probability distribution of assets by sex
active_for_sex = [0.607,0.393] # the first element represents the probability that they are male 

#gender distribution of prefessors 
prefessors_for_sex = [0.689,0.310]

# Population distributions

# positions in the list represents the following ranges: 
# < 5, 5-9, 10-14, 15-19, 20-24, 25-29, 30-64, 65 >
distribution_by_age_groups = [x/total_population for x in [559705, 620358, 578617, 639797, 697891, 722594, 5603201, 1759432]]

# probability distribution of being a woman or a man 
distribution_of_woman_or_man = [0.486,0.496] #the first element represents the probability that they are male

#level of schooling, the first position represents elementary school or less, the second secondary school, 
# the third high school and the last higher education.
distribution_of_schooling = [x/47100 for x in [1952,9995,24713,10440]]


