from simulation.Person import Person
from simulation.Household import Household
from simulation.School import School
# from data_distribution import *

import numpy as np
from multiprocessing import Pool

from data_loader import DataLoader


class World:
    """Environment class where are stored all agents and data for simulation
    Attributes:
    -----------
    neighborhoods (dict):
        dictionary containing a list of Households per province representing "near" houses
    schools (dict):
        dictionary containing another dictionary with a list of schools per type, per province
        'province1': {
            'type1' : [schools]
            ...
        }

    """

    def __init__(self, data_source: DataLoader, n_threads: int = 12):
        """initialization function, crteates world concurrently

        Args:
            data_source (DataLoader): Instance of DataLoader with demographic data
            n_threads (int): number of concurrent threads (default: 12)
        """

        # dictionaries to easy access neighborhoods and schools
        self.neighborhoods = {}
        self.schools = {}
        self.data_source = data_source

        # for i in data_source.provinces_population:
        #     self.generate_neighborhoods(i)
        # multi threaded process to speed up population generation
        with Pool(n_threads) as p:
            results = []
            results.append(p.map(self.generate_neighborhoods,
                                 data_source.provinces_population))

        print(self.neighborhoods)

    def generate_neighborhoods(self, province: str, verbose=0):
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
            self.data_source.provinces_population[province]/(self.data_source.neighborhoods_per_thousand_people*1000))+1

        if verbose >= 2:
            print(province)

        # the neighborhood dictionary gets assigned to the province a list
        # a neighborhood is a list of households, denoting closeness between
        # all hosueholds inside a neighborhood
        self.neighborhoods[province] = []

        # schools in province are organized according to school type
        self.schools[province] = {
            'primary': [],
            'secondary': [],
            'pre_univ': [],
            'university': []
        }

        # according to distribution, number of schools of each type is calculated

        num_of_schools = {
            'primary': self.data_source.provinces_population[province] /
            self.data_source.primary_schools_per_thousand_people,
            'secondary': self.data_source.provinces_population[province] /
            self.data_source.secondary_schools_per_thousand_people,
            'pre_univ': self.data_source.provinces_population[province] /
            self.data_source.pre_universitary_schools_per_thousand_people,
            'university':  self.data_source.universities_per_province
        }

        # for each type of school's number of schools
        # a school is created and stored
        for sc_tp in num_of_schools.keys():
            for _ in range(int(num_of_schools[sc_tp])):
                school = School(province, sc_tp)
                self.schools[province][school.school_type].append(school)

        # the neighborhoods are created
        for j in range(total_neighborhoods):
            cont = 0
            neighborhood = []

            # cont denotes the number of persons in the current neighborhood
            # while its less than the number of persons per neghborhood
            while cont < self.data_source.neighborhoods_per_thousand_people * 1000:
                # a household is created
                h = Household(province, j, self.data_source)
                cont += h.number_of_persons
                has_elder = False
                # all persons in the household get created
                while not has_elder:
                    for _ in range(h.number_of_persons):

                        p = Person(data_source=self.data_source)

                        # a household should have at least one person older than 18
                        # TODO: re implement this
                        if p.age > 18:
                            has_elder = True

                        # if the person is a student, gets assigned to a school
                        # the distribution is assumed uniform to get assigned to a school
                        # given that schools are not located in neighborhoods
                        if p.study:
                            sc = np.random.choice(
                                len(self.schools[province][p.study_details]), 1)[0]
                            self.schools[province][p.study][sc].students.append(
                                p)

                        h.persons.append(p)
                neighborhood.append(h)
            self.neighborhoods[province].append(neighborhood)

        if verbose >= 2:
            print("Finished:", province)
