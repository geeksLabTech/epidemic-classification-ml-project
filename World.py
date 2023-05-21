import json
from time import sleep
import datetime
# from data_distribution import *
from timeit import default_timer as timer
from typing import List
from unittest import result
from asyncpg import Pool


import uuid
from uuid import UUID, uuid4

import numpy as np


from simulation.Person import Person as SimP

from models.household import HouseholdFactory, Household
from models.person import Person, PersonFactory
from models.data_source import DataSource
from models.population import Population
from models.province import Province

from odmantic import SyncEngine, ObjectId
from constants import PRIMARY_SCHOOL, SECONDARY_SCHOOL, PRE_UNIVERSITY_SCHOOL, UNIVERSITY_SCHOOL

db = SyncEngine(database='contact_simulation')

# -> list[Person]:


def create_people_by_household(data_source: DataSource, province: str, household: Household, schools: dict[str, list[str]]):
    # First guarantee that there is at least one adult in the household
    people = [PersonFactory.create(
        data_source, household, schools, province, True)]
    temp = household.number_of_people - 1

    if temp > 0:
        people.extend([PersonFactory.create(
            data_source, household, schools, province) for i in range(temp)])

    db.save_all(people)
    return people


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

    def __init__(self, json_file_path: str):
        """initialization function
        """
        with open(json_file_path, 'r') as j:
            contents = json.loads(j.read())
            self.data_source = DataSource(**contents)

        self.age_groups = np.array(self.data_source.age_groups)

        self.total_population = 0
        self.db = SyncEngine(database='contact_simulation')

        self.politics_deployed = {
            'household': 1,
            'school': 1,
            'work': 1,
            'neighborhood': 0,
            'random place': 1
        }

        # multi threaded process to speed up population generation
        # 16GB RAM dies with 2 threads... use under own responsability
        # with Pool(n_processes) as p:
        #     results = []
        #     results.append(p.map(self.generate_neighborhoods,
        #                          (data_source.provinces_population), 3))

    def get_age_group(self, age: int):
        """
        Get the age group a person belongs to, this is to find the cells in the contact matrix that should be
        updated

        Args:
            age (int): Person's age

        Returns:
            int: index in the age groups matrix
        """

        interval_index = np.where(
            (age >= self.age_groups[:, 0]) & (age <= self.age_groups[:, 1]))[0]

        if interval_index.size > 0:
            interval_index = interval_index[0]
        else:
            interval_index = -1

        return interval_index

    def generate_population(self, population_name: str, n_processes: int = 12):
        """Province by province generate population

        Args:
            population_name (str): Population name, this will be the name to access
            the generated population from the DB
            n_processes (int, optional): Number of concurrent Processes to run. Defaults to 12.
        """

        population = Population(name=population_name, provinces=[])
        provinces = []
        for i in self.data_source.provinces_population:
            start_time = timer()
            # self.generate_province(province=i, n_processes=n_processes)
            provinces.append(self.generate_province(
                i, n_processes=n_processes))
            # provinces.append(p_id)

            print('Finished in', timer() - start_time)
        population.provinces = provinces
        self.db.save(population)

    def generate_province(self, province: str, n_processes: int = 12, verbose=3):
        """generate neigborhoods for a given province

        Args:
            province (str):
                province name, to access province related data and for taggig
                the data generated here
            n_processes (int): number of processes to run concurrently
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
        neighborhoods = []

        # according to distribution, number of schools of each type is calculated

        primary_schools_len = max(int(
            (self.data_source.provinces_population[province]/1000) * self.data_source.primary_schools_per_thousand_people), 1)
        secondary_schools_len = max(int(
            (self.data_source.provinces_population[province]/1000) * self.data_source.secondary_schools_per_thousand_people), 1)
        pre_univ_schools_len = max(int(
            (self.data_source.provinces_population[province]/1000) * self.data_source.pre_universitary_schools_per_thousand_people), 1)
        university_schools_len = max(int(
            self.data_source.universities_per_province), 1)

        schools = {
            PRIMARY_SCHOOL: [str(uuid4()) for _ in range(primary_schools_len)],
            SECONDARY_SCHOOL: [str(uuid4()) for _ in range(secondary_schools_len)],
            PRE_UNIVERSITY_SCHOOL: [str(uuid4()) for _ in range(pre_univ_schools_len)],
            UNIVERSITY_SCHOOL: [str(uuid4())
                                for _ in range(university_schools_len)]
        }
        # province_obj.schools = {
        #     PRIMARY_SCHOOL: [sc.id for sc in schools[PRIMARY_SCHOOL]],
        #     SECONDARY_SCHOOL: [sc.id for sc in schools[SECONDARY_SCHOOL]],
        #     PRE_UNIVERSITY_SCHOOL: [sc.id for sc in schools[PRE_UNIVERSITY_SCHOOL]],
        #     UNIVERSITY_SCHOOL: [sc.id for sc in schools[UNIVERSITY_SCHOOL]]
        # }
        # the neighborhoods are created
        possible_people_by_household = np.arange(start=1, stop=10, step=1)
        inhabitants_distribution = np.array(
            self.data_source.inhabitants_distribution)
        total_households_by_neighborhoods = int(
            1000 / (np.argmax(inhabitants_distribution)+1))
        people_number_by_household = np.random.choice(a=possible_people_by_household,
                                                      p=inhabitants_distribution,
                                                      size=(total_neighborhoods, total_households_by_neighborhoods))

        neighborhoods_ids = [uuid4() for _ in range(people_number_by_household.shape[0])]
        # Create household list from people_number_by_household
        households = [HouseholdFactory.create(neighborhoods_ids[i], province, people_number_by_household[i][j]) for i in range(
            people_number_by_household.shape[0]) for j in range(people_number_by_household.shape[1])]

        # province_obj.households = [h.id for h in households]

        
        start_time = timer()

        for h in households:
            create_people_by_household(self.data_source, province, h, schools)
                
        del households
        del schools

        print('Finished people in ', timer() - start_time)

        start_time = timer()
        people_that_work = [i for i in self.db.find(
            Person, Person.work == True)]
        assert people_that_work is not None
        people_that_work = self.assign_workplaces_to_people(
            len(people_that_work), people_that_work)
    
        self.db.save_all(people_that_work)

        print('Finished workers in ', timer() - start_time)

        if verbose >= 2:
            print("Finished:", province)
        

    def assign_workplaces_to_people(self, total_workers: int, people_that_works: list[Person]):
        workers_count = 0
        workplace_size_by_people = np.random.choice(
            a=[0, 1, 2, 3], size=len(people_that_works))

        people_mask = np.zeros(len(people_that_works))

        while workers_count < total_workers:
            size = np.random.choice(a=[0, 1, 2, 3], size=1)[0]
            wp = str(uuid4())
            for i in range(len(people_that_works)):
                if people_mask[i] == 0 and workplace_size_by_people[i] == size:
                    people_that_works[i].workplace = wp
                    people_mask[i] = 1
                    workers_count += 1

        return people_that_works

    def run_simulation(self, population_name: str, n_days: int = 2, n_processes=12):
        """Code to run simulation, it gets the contacts based on some pre-stablished rules

        Args:
            population_name (str): name of the population to simulate, it will load the simulation from DB
            n_days (int, optional): number of days to simmulate, the more days more accurate should be. Defaults to 2.
            n_processes (int, optional): number of processes to concurrenlty run. Defaults to 12.
        """
        population = self.db.find_one(
            Population, Population.name == population_name)

        if population:
            provinces = population.provinces

            # each day will be divided in 4 moments
            # morning:
            # noon:
            # afternoon:
            # night:

            for i in range(1, n_days):
                for time in ['morning', 'noon', 'afternoon', 'night']:

                    for prov_id in provinces:
                        province = self.db.find_one(
                            Province, Province.id == prov_id)
                        for p_id in province.people:
                            print(p_id)
                            person = self.db.find_one(
                                Person, Person.id == ObjectId(p_id))
                            assert person != None, 'Person cant be None'
                            person_obj = SimP.load_serialized(
                                person.__dict__)
                            person_obj.move(i, time, self.politics_deployed)
