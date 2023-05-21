import json
from time import sleep
import datetime
# from data_distribution import *
from timeit import default_timer as timer
from typing import List
from unittest import result
from asyncpg import Pool
from beanie import WriteRules

import numpy as np
# from multiprocessing import Pool
import multiprocessing
# from pathos import multiprocessing
# from simulation.Person import Person
# from simulation.Household import Household
# from simulation.School import School
# from simulation.workplace import Workplace, WorkplaceSize

from models.person import Person, PersonFactory
from models.household import Household
from models.school import School
from models.workplace import Workplace, WorkplaceFactory
from models.data_source import DataSource

from data_loader import DataLoader
from database.mongodb_client import MongoCRUD
from odmantic import SyncEngine, query
from constants import PRIMARY_SCHOOL, SECONDARY_SCHOOL, PRE_UNIVERSITY_SCHOOL, UNIVERSITY_SCHOOL

db = SyncEngine(database='contact_simulation')

# -> list[Person]:


def create_people_by_household(data_source: DataSource, household: Household, schools: dict[str, list[School]]):
    # First guarantee that there is at least one adult in the household
    people = [PersonFactory.create(data_source, household, schools, True)]
    temp = household.number_of_people - 1

    if temp > 0:
        people.extend([PersonFactory.create(
            data_source, household, schools) for i in range(temp)])

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
        provinces = []

        for i in self.data_source.provinces_population:
            start_time = timer()
            # self.generate_province(province=i, n_processes=n_processes)
            self.generate_province(i, n_processes=n_processes)
            # provinces.append(p_id)

            print('Finished in', timer() - start_time)

        # for i in self.data_source.provinces_population:

        # self.db.insert_one("Population", {"population_name": population_name,
        #                                   "provinces": provinces, "total_population": self.total_population})

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
            PRIMARY_SCHOOL: [School(province=province, school_type=PRIMARY_SCHOOL) for _ in range(primary_schools_len)],
            SECONDARY_SCHOOL: [School(province=province, school_type=SECONDARY_SCHOOL) for _ in range(secondary_schools_len)],
            PRE_UNIVERSITY_SCHOOL: [School(province=province, school_type=PRE_UNIVERSITY_SCHOOL) for _ in range(pre_univ_schools_len)],
            UNIVERSITY_SCHOOL: [School(province=province, school_type=UNIVERSITY_SCHOOL)
                                for _ in range(university_schools_len)]
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

        # Create household list from people_number_by_household
        households = [Household(province=province, number_of_people=people_number_by_household[i][j]) for i in range(
            people_number_by_household.shape[0]) for j in range(people_number_by_household.shape[1])]

        person_list: list[Person] = []
        start_time = timer()

        results = []
        # for h in households:
        #     results.extend(create_people_by_household(self.data_source, h, schools))
        for h in households:
            create_people_by_household(self.data_source, h, schools)

        print('Finished people in ', timer() - start_time)

        start_time = timer()
        people_that_work = [i for i in self.db.find(
            Person, Person.work == True)]
        assert people_that_work is not None
        people_that_work = self.assign_workplaces_to_people(
            province, len(people_that_work), people_that_work)
        self.db.save_all(people_that_work)

        print('Finished workers in ', timer() - start_time)

        # prov_id = self.db.insert_one("Province", {
        #     "province_name": province,
        #     "neighborhoods": neighborhoods,
        #     "schools": inserted_schools,
        #     "workplaces": workplaces
        # }).inserted_id

        if verbose >= 2:
            print("Finished:", province)

        # return prov_id

    def assign_workplaces_to_people(self, province: str, total_workers: int, people_that_works: list[Person]):
        workers_count = 0
        workplace_size_by_people = np.random.choice(
            a=[0, 1, 2, 3], size=len(people_that_works))

        people_mask = np.zeros(len(people_that_works))

        while workers_count < total_workers:
            size = np.random.choice(a=[0, 1, 2, 3], size=1)[0]
            wp = WorkplaceFactory.create(province=province, size=size)
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
        population: dict = self.db.get_one(
            "Population", {"population_name": population_name})

        if population:
            provinces = population['provinces']

            # each day will be divided in 3 possible contact moments
            # 1: At Work/School (contacts related to the workplace and school representing the day for the people in the population)
            # 2: In the neighborhood (contacts in the neighborhood, in this step is assumed contact between friends)
            # 3: In House conttacts (family members)

            for day in range(1, n_days):
                jobs = []
                cont = 0

                print(f"Day: {day}")

                while cont < len(provinces):
                    for _ in range(n_processes):
                        if cont == len(provinces):
                            break
                        p = multiprocessing.Process(
                            target=self.province_execution, args=(population_name, day, provinces[cont]))
                        jobs.append(p)
                        p.start()
                        cont += 1

                    for proc in jobs:
                        proc.join()

    def province_execution(self, population_name: str, day: int, p: str):
        """Iterates over all institutions in a province and generates contacts between the people 
        Contacts are stored in Collection "Contact" in DB

        Args:
            population_name (str): population name to load population from db
            day (int): day of simulation, for more details in contacts
            p (str): province id
        """
        province = self.db.get_one("Province", {"_id": p})

        if 'workplaces' in province:
            for workplace in province['workplaces']:
                pass

        if 'schools' in province:
            for sc_tp in province['schools']:
                # print(province['schools'][sc_tp])
                for school_id in province['schools'][sc_tp]:
                    sch = self.db.get_one(
                        "School", {"_id": school_id})
                    sc_obj = School.load_serialized(sch)

                    pairs = self.generate_contacts(
                        sc_obj.students, 40)
                    self.insert_pairs(day, pairs,  population_name,
                                      str(sc_tp)+' school', province)

        # geenrate contacts in house and store all persons to
        # generate neighborhood contacts
        if 'neighborhoods' in province:
            for n_id in province['neighborhoods']:
                neighborhood = self.db.get_one(
                    'Neighborhood', {"_id": n_id})['neighborhood']
                persons = []

                for house in neighborhood:
                    # print(house)
                    if not 'persons' in house:
                        continue
                    persons.append(house['persons'])
                    pairs = self.generate_contacts(
                        house['persons'], house["number_of_persons"])
                    self.insert_pairs(
                        day, pairs, population_name, "home", province)
                if len(persons) <= 1:
                    continue
                pairs = self.generate_contacts(
                    persons, np.random.randint(5, 30))
                self.insert_pairs(
                    day, pairs, population_name, "neighborhood", province)

    def generate_contacts(self, persons: list, n_contacts: int):  # -> list(tuple(int,int))
        """generate a list of pairs with the ids of people that had contact

        Args:
            persons (list): list of ids of persons to interact
            n_contacts (int): approx ammount of contacts expected to happen between the people 

        Returns:
            list(tuple(str,str)): list of tuples with the ids of both persons that interacted
        """

        if len(persons) < 2:
            return []

        arr = [i for i, j in enumerate(persons)]

        # Repeat each element 30 times
        repeated_arr = np.repeat(arr, n_contacts)
        # Shuffle the repeated array
        np.random.shuffle(repeated_arr)

        # Tile the array to match the repeated length
        tiled_arr = np.tile(arr, n_contacts)

        # Combine the shuffled and tiled arrays to form pairs
        pairs = np.column_stack((repeated_arr, tiled_arr))

        # Filter out reflexive pairs and duplicates
        pairs = pairs[pairs[:, 0] != pairs[:, 1]]
        pairs.sort(axis=1)
        pairs = np.unique(pairs, axis=0)

        pairs = [(persons[pair[0]], persons[pair[1]]) for pair in pairs]

        return pairs

    def insert_pairs(self, day: int, pairs: List, population: str, place: str, province: str):
        """insert a formatted dictionary with relevant info about the contact between two 
        persons

        Args:
            day (int): day of simmulation on which occurs the contact
            pairs (List(tuples(str,str))): list with all pairs of persons interacting between each other
            population (str): population name to access db
            place (str): string deoting type of place in which contact occurred
            province (str): province id to access db
        """

        for p in pairs:
            p1 = self.db.get_one("Person", {"_id": p[0]})
            p2 = self.db.get_one("Person", {"_id": p[1]})

            contact = {
                "day": day,
                "population_name": population,
                "place": place,
                "p1": p1['age'],
                "p2": p2['age'],
                "province": province["province_name"]
            }
            self.db.insert_one("Contact", contact)

    def generate_contact_matrix(self, population_name: str, province: str = None, place: str = None):
        """Generate 

        Args:
            population_name (str): _description_
            province (str, optional): _description_. Defaults to None.
            place (str, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        filt = {"population_name": population_name}
        if province:
            filt['province'] = province
        if place:
            filt['place'] = place

        contacts = self.db.get_data(
            "Contact", filt)

        matrix = np.zeros((len(self.data_source.age_groups),
                           len(self.data_source.age_groups)))

        n_days = 0
        for c in contacts:
            # print(c)
            idx1 = self.get_age_group(c["p1"])
            idx2 = self.get_age_group(c["p2"])
            n_days = max(n_days, c['day'])
            matrix[idx1][idx2] += 1
            matrix[idx2][idx1] += 1

        matrix /= n_days

        total_people = self.db.get_one(
            "Population", {"population_name": population_name})["total_population"]

        for i, row in enumerate(matrix):
            for j, element in enumerate(row):
                factor = (total_people*self.data_source.distribution_by_age_groups[i]) * (
                    total_people*self.data_source.distribution_by_age_groups[j])
                if factor != 0:
                    matrix[i][j] /= factor

        return matrix
