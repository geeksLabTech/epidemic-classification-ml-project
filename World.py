from simulation.Person import Person
from simulation.Household import Household
from simulation.School import School
from data_distribution import *

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import numpy as np
from multiprocessing import Pool


neighborhoods = {}
schools = {}


def generate_neighborhoods(province):

    total_neighborhoods = int(
        provinces_population[province]/(neighborhoods_per_thousand_people*1000))+1
    print(province)

    neighborhoods[province] = []
    schools[province] = {
        'primary': [],
        'secondary': [],
        'pre_univ': [],
        'university': []
    }

    num_of_primary_schools = provinces_population[province] / \
        primary_schools_per_thousand_people
    num_of_secondary_schools = provinces_population[province] / \
        secondary_schools_per_thousand_people
    num_of_pre_universitary_schools = provinces_population[province] / \
        pre_universitary_schools_per_thousand_people
    num_universities = universities_per_province
    num_of_schools = {
        'primary': num_of_primary_schools,
        'secondary': num_of_secondary_schools,
        'pre_univ': num_of_pre_universitary_schools,
        'university': num_universities
    }

    for t in num_of_schools:
        for j in range(num_of_schools[t]):
            school = School(province, t)
            schools[province][school.school_type].append(school)

    for j in range(total_neighborhoods):
        cont = 0
        neighborhood = []

        while cont < neighborhoods_per_thousand_people * 1000:
            h = Household(province, j)
            cont += h.number_of_persons
            for _ in range(h.number_of_persons):

                p = Person()

                if p.study:
                    sc = np.random.choice(
                        len(schools[province][p.study]), 1)[0]
                    schools[province][p.study][sc].students.append(p)

                h.persons.append(p)
            neighborhood.append(h)
        neighborhoods[province].append(neighborhood)
    print("Finished:", province)


with Pool(12) as p:
    results = []
    results.append(p.map(generate_neighborhoods, provinces_population))

print(neighborhoods)
