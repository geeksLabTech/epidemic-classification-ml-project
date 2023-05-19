from time import sleep
import datetime
from simulation.workplace import Workplace, WorkplaceSize
# from data_distribution import *
from timeit import default_timer as timer
from typing import List, Literal, Any

import numpy as np
from multiprocessing import Pool
import multiprocessing

from simulation.Person import Person
from simulation.Household import Household
from simulation.School import School
from simulation.workplace import Workplace, WorkplaceSize

from data_loader import DataLoader
from database.mongodb_client import MongoCRUD


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
        # with Pool(n_processes) as p:
        #     results = []
        #     results.append(p.map(self.generate_neighborhoods,
        #                          (data_source.provinces_population), 3))

    def __create_and_serialize_household(self, province, number_of_people: int, neighborhood, people_by_school_type, people_that_work: list):
        adult = [Person(self.data_source, True).serialize()]
        temp = number_of_people - 1

        if temp > 0:
            people = [Person(self.data_source).serialize()
                      for _ in range(temp)]
            people_ids = self.db.insert_many(
                'Person', people+adult).inserted_ids
            for i in range(len(people)):
                if 'work' in people[i] == True:
                    people_that_work.append(people_ids[i])
                if 'study_details' in people[i]:
                    if not people[i]['study_details'] in people_by_school_type:
                        people_by_school_type[people[i]['study_details']] = []
                    people_by_school_type[people[i]['study_details']].append(
                        people_ids[i])
                    # print('entro', people_by_school_type)
        else:
            people_ids = [self.db.insert_one('Person', adult[0]).inserted_id]
            if 'work' in adult[0] == True:
                people_that_work.append(people_ids[0])
            if 'study_details' in adult[0]:
                if not adult[0]['study_details'] in people_by_school_type:
                    people_by_school_type[adult[0]['study_details']] = []
                people_by_school_type[adult[0]
                                      ['study_details']].append(people_ids[0])

        # print('people by school type', people_by_school_type[province])
        # print(len(people_by_school_type['primary']), len(people_by_school_type['secondary']), len(people_by_school_type['pre_univ']), len(people_by_school_type['university']))
        h = Household(province, neighborhood, self.data_source,
                      people_ids, number_of_people)
        return h.serialize(), people_by_school_type, people_that_work

    def parallel_household_creation(self, people_number_by_household, province, i, household_by_neighborhood: dict, people_by_school_type: dict, people_that_work: list):
        # print(f'started proccess {i}')
        households = []

        for j in range(people_number_by_household.shape[1]):
            temp = {
                'primary': [],
                'secondary': [],
                'pre_univ': [],
                'university': []
            }
            h, temp, people_that_work_to_add = self.__create_and_serialize_household(
                province, people_number_by_household[i][j], i, temp, [])
            households.append(h)
            people_by_school_type.update(temp)
            people_that_work.extend(people_that_work_to_add)
            # for sc_tp in new_people_by_school_type[province]:
            #     people_by_school_type[province][sc_tp].extend(new_people_by_school_type[province][sc_tp])

        household_by_neighborhood[i] = households
        # print(f'finished proccess {i}')

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
            p_id = self.generate_province(i, n_processes=n_processes)
            provinces.append(p_id)

            print('Finished in', timer() - start_time)

        # for i in self.data_source.provinces_population:

        self.db.insert_one("Population", {"population_name": population_name,
                                          "provinces": provinces, "total_population": self.total_population})

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
        people_that_work = manager.list()

        schools['primary'] = []
        schools['secondary'] = []
        schools['pre_univ'] = []
        schools['university'] = []
        inserted_schools = {}

        jobs = []

        i = 0
        context = multiprocessing.get_context('fork')
        while i < (people_number_by_household.shape[0]):
            for _ in range(n_processes):
                if i == people_number_by_household.shape[0]:
                    break
                i += 1
                p = context.Process(target=self.parallel_household_creation, args=(
                    people_number_by_household, province, i, households_by_neighborhood_dict, schools, people_that_work))
                jobs.append(p)
                p.start()

            for proc in jobs:
                proc.join()

        for key in households_by_neighborhood_dict:
            n_id = self.db.insert_one("Neighborhood", {
                                      "neighborhood": households_by_neighborhood_dict[key][0]}).inserted_id
            neighborhoods.append(n_id)

        for key in schools:
            if len(schools[key]) == 0:
                print(f'school of type {key} in {province} empty')
                continue

            students_id_assigned = np.random.choice(a=np.arange(
                num_of_schools['primary']), size=len(schools[key]))
            inserted_schools[key] = self.build_and_save_schools(
                key, province, students_id_assigned, schools[key])

        works_by_people = np.random.choice(
            a=[0, 1, 2, 3], size=len(people_that_work))
        people_mask = np.zeros(len(works_by_people))
        total_workers = 0

        # Find a way to calculate this value
        workplaces_by_province = 0.8

        # test this code later
        workplaces = []
        while total_workers < len(people_that_work):
            temp: Literal[0,1,2,3] = np.random.choice([0, 1, 2, 3])
            wp = Workplace(province=province, size=WorkplaceSize(temp))

            assigned_people = []
            for i in range(len(works_by_people)):
                if people_mask[i] == 0 and works_by_people[i] == temp:
                    assigned_people.append(people_that_work[i])
                    people_mask[i] = 1
                    if wp.number_of_people == len(assigned_people):
                        # salir del ciclo si ya se lleno el centro de trabajo
                        break
            wp.fill_with_people(assigned_people)

            wp_id = self.db.insert_one('Workplace', wp.serialize()).inserted_id
            total_workers += len(assigned_people)
            workplaces.append(wp_id)

        prov_id = self.db.insert_one("Province", {
            "province_name": province,
            "neighborhoods": neighborhoods,
            "schools": inserted_schools,
            "workplaces": workplaces
        }).inserted_id

        if verbose >= 2:
            print("Finished:", province)

        return prov_id

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
        return self.db.insert_many("School", schools_to_insert).inserted_ids

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
            for workplace_id in province['workplaces']:
                workplace_dict: dict[str, Any] = self.db.get_one('Workplace',
                                                                 {'_id': workplace_id})
                workplace = Workplace.load_serialized(workplace_dict)

                pairs=self.generate_contacts(
                    workplace.workers_ids,
                    np.random.randint(0,workplace.number_of_people))

                self.insert_pairs(day,
                                  pairs,
                                  population_name,
                                  str(workplace_id)+' workplace',
                                  province)

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
                    if 'persons' not in house:
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
