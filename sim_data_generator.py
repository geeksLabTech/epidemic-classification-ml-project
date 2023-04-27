import random
from data_distribution import *


def generate_population(age_distribution, total_population):
    # Calculate the number of individuals in each age group
    num_individuals = [int(coeff * total_population)
                       for coeff in age_distribution]

    # Generate individuals for each age group using random sampling
    population = []
    for i, num in enumerate(num_individuals):
        if i == 7:  # last age group includes all ages 35 and above
            age_range = range(35, 120)  # assuming maximum age is 120
        else:
            age_range = range(i*5, i*5+5)
        for j in range(num):
            age = random.choice(age_range)
            population.append(age)

    return population


pop = generate_population(distribution_by_age_groups, 1000)

employment_by_age = {}
enrollment_by_age = {
    1: 24086,
    2: 28229,
    3: 31688,
    4: 32443,
    5: 21124,
    6: 21588,
}

for i in pop:

    # until secondary school all people in age must go to the corresponding school
    if i <= 15:
        if i in enrollment_by_age:
            enrollment_by_age[i] += 1
        else:
            enrollment_by_age[i] = 1
    # pre-universitary is assigned according to the distribution
    if i > 15 and i < 18:
        if random.random() < enrollment_distribution[2]/total_population:
            if i in enrollment_by_age:
                enrollment_by_age[i] += 1
            else:
                enrollment_by_age[i] = 1
    # for university, in case of a person being over 30 years the probability is gradually reduced
    if i > 18:
        population_coef = total_population
        if i > 30:
            population_coef *= i/10
        if random.random() < enrollment_distribution[3]/population_coef:
            if i in enrollment_by_age:
                enrollment_by_age[i] += 1
            else:
                enrollment_by_age[i] = 1

    if i > 15 and i < 75 and random.random() <= active_man_in_working_age[0]:
        if i in employment_by_age:
            employment_by_age[i] += 1
        else:
            employment_by_age[i] = 1

age_groups = [
    [0, 4], [5, 9], [10, 14], [15, 19], [20, 24], [25, 29], [30, 34], [
        35, 39], [40, 44], [45, 49], [50, 54], [55, 59], [60, 64],  [65, 100]
]

data = {
    "location_name": "cuba",
    "data_provenance_notices": [],
    "reference_links": [],
    "citations": [],
    "notes": [],
    "parent": None,
    "population_age_distributions": [{
        "num_bins": 8,
        "distribution": [
            age_g.append(distribution_by_age_groups[idx]) for idx, age_g in age_groups
        ]
    }],
    "employment_rates_by_age": [
        [i, employment_by_age[i]] for i in employment_by_age

    ],
    "enrollment_rates_by_age": [
        [i, enrollment_by_age[i]] for i in enrollment_by_age
    ],
    "household_head_age_brackets": [],
    "household_head_age_distribution_by_family_size": [],
    "household_size_distribution": [
    ],
    "ltcf_resident_to_staff_ratio_distribution": [],
    "ltcf_num_residents_distribution": [],
    "ltcf_num_staff_distribution": [],
    "ltcf_use_rate_distribution": [],
    "school_size_brackets": [],
    "school_size_distribution": [],
    "school_size_distribution_by_type": [],
    "school_types_by_age": [{
        "school_type": "ps",
        "age_range": [0, 4]
    }, {
        "school_type": "es",
        "age_range": [5, 11]
    }, {
        "school_type": "se",
        "age_range": [12, 15]
    }, {
        "school_type": "pu",
        "age_range": [16, 17]
    }, {
        "school_type": "uv",
        "age_range": [18, 100]
    }],
    "workplace_size_counts_by_num_personnel": [
    ]
}
