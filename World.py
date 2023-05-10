from simulation.Person import Person
from simulation.Household import Household
from simulation.School import School
from data_distribution import *

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import numpy as np
from multiprocessing import Pool

# dictionaries to easy access neighborhoods and schools
neighborhoods = {}
schools = {}


def generate_neighborhoods(province, verbose=0):
    """generate neigborhoods for a given province

    Args:
        province (str): 
            province name, to access province related data and for taggig 
            the data generated here 
        verbose (int):
            integer denoting log level, for debug proposes (default: 0)
    """

    # according to distribution, the province population is divided by
    # the number of people per neighborhood
    # resulting on the number of neighborhoods in the province
    total_neighborhoods = int(
        provinces_population[province]/(neighborhoods_per_thousand_people*1000))+1

    if verbose >= 2:
        print(province)

    # the neighborhood dictionary gets assigned to the province a list
    # a neighborhood is a list of households, denoting closeness between
    # all hosueholds inside a neighborhood
    neighborhoods[province] = []

    # schools in province are organized according to school type
    schools[province] = {
        'primary': [],
        'secondary': [],
        'pre_univ': [],
        'university': []
    }

    # according to distribution, number of schools of each type is calculated
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

    # for each type of school's number of schools
    # a school is created and stored
    for t in num_of_schools.keys():
        for _ in range(num_of_schools[t]):
            school = School(province, t)
            schools[province][school.school_type].append(school)

    # the neighborhoods are created
    for j in range(total_neighborhoods):
        cont = 0
        neighborhood = []

        # cont denotes the number of persons in the current neighborhood
        # while its less than the number of persons per neghborhood
        while cont < neighborhoods_per_thousand_people * 1000:
            # a household is created
            h = Household(province, j)
            cont += h.number_of_persons
            has_elder = False
            # all persons in the household get created
            while not has_elder:
                for _ in range(h.number_of_persons):

                    p = Person()

                    # a household should have at least one person older than 18
                    # TODO: re implement this
                    if p.age > 18:
                        has_elder = True

                    # if the person is a student, gets assigned to a school
                    # the distribution is assumed uniform to get assigned to a school
                    # given that schools are not located in neighborhoods
                    if p.study:
                        sc = np.random.choice(
                            len(schools[province][p.study_details]), 1)[0]
                        schools[province][p.study][sc].students.append(p)

                    h.persons.append(p)
            neighborhood.append(h)
        neighborhoods[province].append(neighborhood)
    \
    if verbose >= 2:
        print("Finished:", province)


# multi threaded process to speed up population generation
with Pool(12) as p:
    results = []
    results.append(p.map(generate_neighborhoods, provinces_population))

print(neighborhoods)
