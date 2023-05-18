# work-related distributions

districts_population = {
    "HK Island-Central and Western": 235953,
    "HK Island-Wan Chai": 166695,
    "HK Island-Eastern": 529603,
    "HK Island-Southern": 263278,
    "Kowloon-Yau Tsim Mong":310647,
    "Kowloon-Sham Shui Po": 431090,
    "Kowloon-Kowloon City": 410634,
    "Kowloon-Wong Tai Sin": 406802,
    "Kowloon-Kwun Tong": 673166,
    "New Territories-Kwai Tsing": 495798,
    "New Territories-Tsuen Wan": 320094,
    "New Territories-Tuen Mun": 506879,
    "New Territories-Yuen Long": 668080,
    "New Territories-North": 309631,
    "New Territories-Tai Po": 316470,
    "New Territories-Sha Tin": 692806,
    "New Territories-Sai Kung": 489037,
    "New Territories-Islands": 185282,
    "Marine": 1125,
}
total_employees = 3613200
teacher_number = 73077
total_population = 7412166
female_population = 3997135
male_population = 3415031

# probability distribution of active persons with respect to the total population 
# the first element represents the probability that they are active
active_man_in_total_population = [0.519,0.48]

# probability distribution of active people of working age (15 and over)
# the first element represents the probability that are active
active_people_in_working_age = [3613200/6580600, 1-(3613200/6655400)]

# probability distribution of men and women of working age
# the first element represents the probability that they are male
working_age = [2953900/6580600, 3626700/6580600]

# distribution of the probability of being active if you are a woman
# the first element represents the probability that they are active
active_woman_in_working_age = [1823700/3626700, 1-(1823700/3626700)]

# distribution of the probability of being active if you are a man
# the first element represents the probability that they are active
active_man_in_working_age = [1789500/2953900, 1-(1789500/2953900)]

# probability distribution of assets by sex
# the first element represents the probability that they are male
active_by_sex = [1789500/3613200, 1823700/3613200]

# gender distribution of professors,  first position refers to women
professors_by_sex = [52148/73077, 20929/73077]

primary_schools_per_thousand_people = 591 / (total_population/1000)
secondary_schools_per_thousand_people = 514 / (total_population/1000)
post_secundary_colleges= 18 / (total_population / 1000)
universities_per_province = 10 / 15

# Distribution of persons by economic activity (both sexes)
# positions in the list represents the following labels:
# 0 Manufacturing
# 1 Construction
# 2 Import/export, wholesale and retail trades
# 3 Transportation, storage, postal and courier services
# 4 Accommodation and food services
# 5 Information and communications
# 6 Financing and insurance
# 7 Real state, professional and business services
# 8 Public administration, education, human health and social work activities
# 9 Miscellaneous social and personal services
# 10 Others

distribution_by_activity_economic = [0.031,0.086,0.155,0.082,0.07,0.036,0.076,0.158,0.177,0.123,0.06]

# Distribution of women by economic activity
# The positions represent the same as in the previous distribution
women_distribution_by_activity_economic = [ 43965/1886433, 42357/1886433, 317407/1886433, 65392/1886433, 134495/1886433, 40932/1886433,
                                            149009/1886433, 298378/1886433, 398078/1886433,  390587/1886433,  5833/1886433]

# Distribution of man by economic activity
# The positions represent the same as in the previous distribution
men_distribution_by_economic_activity =[ 71012/1794862, 274679/1794862, 254095/1794862, 237109/1794862, 123956/1794862, 90787/1794862,
                                         130327/1794862, 282265/1794862, 252494/1794862, 61048/1794862, 17090/1794862]


# Population distributions

# positions in the list represents the following ranges:
# < 5, 5-9, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39,40-44, 45-49, 50-54, 55-59,60-64,65-69,70-74,75-79,80-84,>=85>
distribution_by_age_groups = [0.032,0.04,0.039,0.035,0.046,0.063,0.072,0.08,0.079,0.078,0.077,0.085,0.083,0.064,0.048,0.025,0.023,0.03]

# probability distribution of being a woman or a man
# the first element represents the probability that they are male
distribution_of_man_or_woman = [0.456, 0.544]

# level of study, the first position represents primary and below, lower secondary , upper secondary, 
# post-secundary (diploma/certificate), post-secondary(sub-degree course) and post secondary (degree course) in that order.
enrollment_distribution = [0.184,0.171,0.299,0.057,0.051,0.237]

age_groups = [
    [0, 4], [5, 9], [10, 14], [15, 19], [20, 24], [25, 29], [30, 34], [
        35, 39], [40, 44], [45, 49], [50, 54], [55, 59], [60, 64],  [65, 69], [70, 74], [75, 79], [80, 84] , [85, 100]
]
# number of members per home variable.
# Position i represents the number of homes with i+1 members
total_houses = 2674161

#urban_rural = [2894708, 890488]

# to be checked
neighborhoods_per_thousand_people = 1.0

prob_density = [elem/total_houses for elem in [ 541152, 766632, 641187, 456067, 191927, 77196]]
