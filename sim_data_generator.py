import random
from data_distribution import *
data = {
    "location_name": "",
    "data_provenance_notices": [],
    "reference_links": [],
    "citations": [],
    "notes": [],
    "parent": None,
    "population_age_distributions": [{
        "num_bins": 8,
        "distribution": [
        ]
    }],
    "employment_rates_by_age": [
    ],
    "enrollment_rates_by_age": [
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
        "age_range": [3, 4]
    }, {
        "school_type": "pr",
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

# data['population_age_distributions'][0]['distribution'] =

# Define the total population size


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
