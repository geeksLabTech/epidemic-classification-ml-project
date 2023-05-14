from responses import start
from simulation.Person import Person
from simulation.Household import Household
from simulation.School import School
# from simulation.workplace import Workplace, WorkplaceSize
# from data_distribution import *

import pickle
import numpy as np
from multiprocessing import Pool

from data_loader import DataLoader
from database.mongodb_client import MongoCRUD
# import time 
from timeit import default_timer as timer

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
    workplaces (dict):
        dictionary containing a list of workplaces per province
    """

    def __init__(self, data_source: DataLoader, n_threads: int = 12):
        """initialization function, crteates world concurrently

        Args:
            data_source (DataLoader): Instance of DataLoader with demographic data
            n_threads (int): number of concurrent threads (default: 1)
        """
        # dictionaries to easy access neighborhoods and schools
        self.data_source = data_source
        self.person_id = 1
        self.house_id = 1
        self.neighborhood_id = 1
        self.db = MongoCRUD('contact_simulation')
        for i in data_source.provinces_population:
            start_time = timer()
            self.generate_neighborhoods(i)
            
            print('termino en ', timer() - start_time)
        # multi threaded process to speed up population generation
        # 16GB RAM dies with 2 threads... use under own responsability
        # with Pool(n_threads) as p:
        #     results = []
        #     results.append(p.map(self.generate_neighborhoods,
        #                          (data_source.provinces_population), 3))


    def __create_household_people(self, data_source: DataLoader, number_of_people: int):
        adult = [Person(self.data_source, True)]
        temp = number_of_people - 1
        if temp > 0 :
            people = [Person(self.data_source) for _ in range(temp)]
            return adult + people
        return adult
    

    def generate_neighborhoods(self, province: str, verbose=3):
        """generate neigborhoods for a given province

        Args:
            province (str): 
                province name, to access province related data and for taggig 
                the data generated here 
            verbose (int):
                integer denoting log level, for debug proposes (default: 0)
        """

        neighborhoods = {}
        schools = {}
        # workplaces: dict[str, list[Workplace]] = {}
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
        neighborhoods[province] = []

        # schools in province are organized according to school type
        schools[province] = {
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
        # for sc_tp in num_of_schools.keys():
        #     for _ in range(int(num_of_schools[sc_tp])):
        #         school = School(province, sc_tp)
        #         self.db.insert_data("School", school.serialize())
        #         del school

        # the neighborhoods are created

        people_by_neighborhood = int
        possible_people_by_household = np.arange(start=1, stop=10, step=1)
        inhabitants_distribution = np.array(self.data_source.inhabitants_distribution)
        for j in range(total_neighborhoods):
            # print(j, '/', total_neighborhoods)
            cont = 0
            neighborhood = []

            people_number_by_household = np.random.choice(a=possible_people_by_household,
                                                p=inhabitants_distribution,
                                                size=200)
            
            current_people = np.sum(people_number_by_household)

            if current_people < int(self.data_source.neighborhoods_per_thousand_people) * 1000:
                mean = current_people / len(people_number_by_household)
                temp = int(self.data_source.neighborhoods_per_thousand_people) * 1000 - current_people
                # print('a', possible_people_by_household)
                # print('p', inhabitants_distribution)
                # print('temp', temp, mean, int(temp/mean))
                extra_households = np.random.choice(a=possible_people_by_household,
                                                p=inhabitants_distribution,
                                                size=int(temp/mean))
                people_number_by_household = np.concatenate((people_number_by_household, extra_households))

            people_by_household = [self.__create_household_people(self.data_source, i) for i in people_number_by_household]
            serialized_people = [[p.serialize() for p in household] for household in people_by_household]
            people_id_by_household = [self.db.insert_many("Person", p_list).inserted_ids for p_list in serialized_people]
            households = [Household(province, j, i, self.data_source, people_id_by_household[i]) for i in range(len(people_by_household))]
            neighborhood = [h.serialize() for h in households]
            n_id = self.db.insert_one("Neighborhood", {"neighborhood": neighborhood}).inserted_id
            neighborhoods[province].append(n_id)

            
                        # if the person is a student, gets assigned to a school
                        # the distribution is assumed uniform to get assigned to a school
                        # given that schools are not located in neighborhoods
                        # if p.study:
                        #     sc = np.random.choice(
                        #         len(schools[province][p.study_details]), 1)[0]
                        #     schools[province][p.study_details][sc].students.append(
                        #         p.id)

        self.db.insert_one("Province", {province: neighborhoods[province]})

        # Find a way to calculate this value
        workplaces_by_province = 0.8

        # test this code later
        # workplaces[province] = []
        # total_workers = 0
        # id = 0
        # while total_workers < self.data_source.provinces_population[province] * workplaces_by_province:
        #     temp = np.random.choice([0,1,2,3])
        #     match temp:
        #         case 0: size = WorkplaceSize.SMALL
        #         case 1: size = WorkplaceSize.MEDIUM
        #         case 2: size = WorkplaceSize.LARGE
        #         case 3: size = WorkplaceSize.EXTRA_LARGE
        #     wp = Workplace(id, province, size)
        #     total_workers += wp.number_of_people
        #     workplaces[province].append(wp)

        # with open(f"population_data/{province}.pickle", "wb") as f:
        #     pickle.dump(
        #         {"neighborhoods": neighborhoods, "schools": schools}, f)

        if verbose >= 2:
            print("Finished:", province)
