
from simulation.Person import Person
from simulation.Household import Household
from simulation.School import School
from time import sleep
import datetime
# from simulation.workplace import Workplace, WorkplaceSize
# from data_distribution import *

# import pickle
import numpy as np
from multiprocessing import Pool
import multiprocessing

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

    def __init__(self, data_loader: DataLoader):
        """initialization function
        """

        self.data_source = data_loader

        self.age_groups = np.array(self.data_source.age_groups)

        self.total_population = 0
        self.db = MongoCRUD('contact_simulation')

        # multi threaded process to speed up population generation
        # 16GB RAM dies with 2 threads... use under own responsability
        # with Pool(n_threads) as p:
        #     results = []
        #     results.append(p.map(self.generate_neighborhoods,
        #                          (data_source.provinces_population), 3))

    def __create_and_serialize_household(self, province, number_of_people: int, neighborhood, people_by_school_type):
        adult = [Person(self.data_source, True).serialize()]
        temp = number_of_people - 1
        if temp > 0:
            people = [Person(self.data_source).serialize()
                      for _ in range(temp)]
            people_ids = self.db.insert_many(
                'Person', people+adult).inserted_ids
            for i in range(len(people)):
                if 'study_details' in people[i]:
                    if not people[i]['study_details'] in people_by_school_type:
                        people_by_school_type[people[i]['study_details']] = []
                    people_by_school_type[people[i]['study_details']].append(
                        people_ids[i])
                    # print('entro', people_by_school_type)
        else:
            people_ids = [self.db.insert_one('Person', adult[0]).inserted_id]
            if 'study_details' in adult[0]:
                if not adult[0]['study_details'] in people_by_school_type:
                    people_by_school_type[adult[0]['study_details']] = []
                people_by_school_type[adult[0]
                                      ['study_details']].append(people_ids[0])

        # print('people by school type', people_by_school_type[province])
        # print(len(people_by_school_type['primary']), len(people_by_school_type['secondary']), len(people_by_school_type['pre_univ']), len(people_by_school_type['university']))
        h = Household(province, neighborhood, self.data_source,
                      people_ids, number_of_people)
        return h.serialize(), people_by_school_type

    def parallel_household_creation(self, people_number_by_household, province, i, household_by_neighborhood: dict, people_by_school_type: dict):
        # print(f'started proccess {i}')
        households = []
        temp = {
            'primary': [],
            'secondary': [],
            'pre_univ': [],
            'university': []
        }
        for j in range(people_number_by_household.shape[1]):
            h = self.__create_and_serialize_household(
                province, people_number_by_household[i][j], i, temp)
            households.append(h)
            people_by_school_type.update(temp)
            # for sc_tp in new_people_by_school_type[province]:
            #     people_by_school_type[province][sc_tp].extend(new_people_by_school_type[province][sc_tp])

        household_by_neighborhood[i] = households
        # print(f'finished proccess {i}')

    def get_age_group(self, age: int):
        interval_index = np.where(
            (age >= self.age_groups[:, 0]) & (age <= self.age_groups[:, 1]))[0]

        if interval_index.size > 0:
            interval_index = interval_index[0]
        else:
            interval_index = -1
        return interval_index

    def generate_population(self, population_name: str, n_threads: int = 12):

        for i in self.data_source.provinces_population:
            start_time = timer()
            self.generate_province(province=i)

            print('Finished in', timer() - start_time)

        provinces = []

        for i in self.data_source.provinces_population:
            provinces.append(self.generate_province(i, n_threads=n_threads))

        self.db.insert_one("Population", {"population_name": population_name,
                                          "provinces": provinces, "total_population": self.total_population})

    def generate_province(self, province: str, n_threads: int = 12, verbose=3):
        """generate neigborhoods for a given province

        Args:
            province (str):
                province name, to access province related data and for taggig
                the data generated here
            verbose (int):
                integer denoting log level, for debug proposes (default: 0)
        """

        neighborhoods = {}
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

        # according to distribution, number of schools of each type is calculated

        num_of_schools = {
            'primary': (self.data_source.provinces_population[province]/1000) *
            self.data_source.primary_schools_per_thousand_people,
            'secondary': (self.data_source.provinces_population[province]/1000) *
            self.data_source.secondary_schools_per_thousand_people,
            'pre_univ': (self.data_source.provinces_population[province] / 1000) *
            self.data_source.pre_universitary_schools_per_thousand_people,
            'university':  self.data_source.universities_per_province
        }

        # the neighborhoods are created
        possible_people_by_household = np.arange(start=1, stop=10, step=1)
        inhabitants_distribution = np.array(
            self.data_source.inhabitants_distribution)
        total_households_by_neighborhoods = int(
            1000 / (np.argmax(inhabitants_distribution)+1))
        people_number_by_household = np.random.choice(a=possible_people_by_household,
                                                      p=inhabitants_distribution,
                                                      size=(total_neighborhoods, total_households_by_neighborhoods))

        manager = multiprocessing.Manager()
        households_by_neighborhood_dict = manager.dict()
        schools = manager.dict()

        # schools in province are organized according to school type
        # schools[province] = {
        #     'primary': [],
        #     'secondary': [],
        #     'pre_univ': [],
        #     'university': []
        # }
        schools['primary'] = []
        schools['secondary'] = []
        schools['pre_univ'] = []
        schools['university'] = []

        jobs = []

        for i in range(people_number_by_household.shape[0]):
            p = multiprocessing.Process(target=self.parallel_household_creation, args=(
                people_number_by_household, province, i, households_by_neighborhood_dict, schools))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()

        for key in households_by_neighborhood_dict:
            n_id = self.db.insert_one("Neighborhood", {
                                      "neighborhood": households_by_neighborhood_dict[key]}).inserted_id
            neighborhoods[province].append(n_id)

        for key in schools:
            if len(schools[key]) == 0:
                print(f'school of type {key} in {province} empty')
                continue

            students_id_assigned = np.random.choice(a=np.arange(
                num_of_schools['primary']), size=len(schools[key]))
            self.build_and_save_schools(
                key, province, students_id_assigned, schools[key])

        # self.db.insert_one("Province", {province: neighborhoods[province]})

        # Find a way to calculate this value
        workplaces_by_province = 0.8

        # test this code later
        workplaces = []
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
        prov_id = self.db.insert_one("Province", {
            province: {
                "neighborhoods": neighborhoods,
                "schools": schools,
                "workplaces": workplaces
            }
        }).inserted_id

        if verbose >= 2:
            print("Finished:", province)

    def build_and_save_schools(self, school_type: str, province: str, students_id_assigned, students_id: list):
        splitted_students_by_school = {}
        # print('len(students_id_assigned)', len(students_id_assigned))
        for i in range(len(students_id_assigned)):
            if students_id_assigned[i] not in splitted_students_by_school:
                splitted_students_by_school[students_id_assigned[i]] = []
            splitted_students_by_school[students_id_assigned[i]].append(
                students_id[i])

        schools_to_insert = [School(province, school_type, splitted_students_by_school[key]).serialize(
        ) for key in splitted_students_by_school]
        # print('len(schools_to_insert)', len(schools_to_insert))
        self.db.insert_many("School", schools_to_insert)
