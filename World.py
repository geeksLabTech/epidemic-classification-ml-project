import json
import uuid
from multiprocessing import Pool
# from data_distribution import *
from timeit import default_timer as timer
from uuid import UUID

import numpy as np
from odmantic import ObjectId, SyncEngine

from constants import (PRE_UNIVERSITY_SCHOOL, PRIMARY_SCHOOL, SECONDARY_SCHOOL,
                       UNIVERSITY_SCHOOL)
from models.action import Action
from models.person import Person, PersonFactory, create_parallel, move_person
from models.place import Place
from models.population import Population
from models.data_source import DataSource
# from pathos import multiprocessing
# from data_loader import DataLoader
# from simulation.Person import Person as SimP

# from simulation.Household import Household
# from simulation.School import School
# from simulation.workplace import Workplace, WorkplaceSize


db = SyncEngine(database='contact_simulation_2n', )


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

    def __init__(self, json_file_path: str | None = None, data_source: DataSource | None = None):
        """initialization function
        """
        if data_source is None:
            if json_file_path is None:
                raise ValueError(
                    'json_file_path and data_source cannot be None at the same time')
            with open(json_file_path, 'r') as j:
                contents = json.loads(j.read())

            self.data_source = DataSource(**contents)

        else:
            self.data_source = data_source

        # self.data_source = DataSource()
        # self.data_source.vectorize_data()

        self.age_groups = np.array(self.data_source.age_groups)
        self.people_that_work = []

        self.mat = {
            "work": np.zeros((len(self.data_source.age_groups),
                              len(self.data_source.age_groups))),
            "school": np.zeros((len(self.data_source.age_groups),
                                len(self.data_source.age_groups))),
            "neighborhood": np.zeros((len(self.data_source.age_groups),
                                      len(self.data_source.age_groups))),
            "house": np.zeros((len(self.data_source.age_groups),
                               len(self.data_source.age_groups)))
        }

        self.mat_ages = np.ones(len(self.data_source.age_groups))

        self.total_population = 0
        self.db = SyncEngine(database='contact_simulation_2n')

        self.politics_deployed = {
            'household': 1,
            'school': 1,
            'workplace': 1,
            'neighborhood': 1,
            'random place': 1
        }

        # multi threaded process to speed up population generation
        # 16GB RAM dies with 2 threads... use under own responsability
        # with Pool(n_processes) as p:
        #     results = []
        #     results.append(p.map(self.generate_neighborhoods,
        #                          (data_source.provinces_population), 3))

    def create_people_by_household(self, prov_id: str, data_source: DataSource, household: dict, schools: dict[str, list[UUID]]):
        # First guarantee that there is at least one adult in the household
        people = [PersonFactory.create(
            data_source, household, schools, prov_id, True)]
        temp = household['number_of_people'] - 1
        if people[0].work == True:
            self.people_that_work.append(people[0])
        if temp > 0:
            for i in range(temp):
                pers_i = PersonFactory.create(
                    data_source, household, schools, prov_id)
                if pers_i.work == True:
                    self.people_that_work.append(pers_i)
                people.append(pers_i)
                self.mat_ages[people[-1].age_group] += 1

        db.save_all(people)

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
        provinces = {}
        for i in self.data_source.provinces_population:
            provinces[i] = str(uuid.uuid4())
            start_time = timer()
            # self.generate_province(province=i, n_processes=n_processes)
            self.generate_province(
                i, provinces[i], n_processes=n_processes)
            # provinces.append(p_id)

            print('Finished in', timer() - start_time)
        population.provinces = provinces
        self.db.save(population)
        self.population_name = population_name
        # for i in self.data_source.provinces_population:

        # self.db.insert_one("Population", {"population_name": population_name,
        #                                   "provinces": provinces, "total_population": self.total_population})

    def generate_province(self, province: str, prov_id: str, n_processes: int = 12, verbose=3):
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
            # print(total_neighborhoods)

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
            PRIMARY_SCHOOL: [],
            SECONDARY_SCHOOL: [],
            PRE_UNIVERSITY_SCHOOL: [],
            UNIVERSITY_SCHOOL: []
        }

        places = []
        list_ids = []
        for _ in range(primary_schools_len):
            p_id = str(uuid.uuid4())
            list_ids.append(p_id)
            places.append(
                Place(place=p_id, province=prov_id, clasification="school"))

        schools[PRIMARY_SCHOOL] = list_ids
        list_ids = []
        for _ in range(secondary_schools_len):
            p_id = str(uuid.uuid4())
            list_ids.append(p_id)
            places.append(
                Place(place=p_id, province=prov_id, clasification="school"))

        schools[SECONDARY_SCHOOL] = list_ids
        list_ids = []
        for _ in range(pre_univ_schools_len):
            p_id = str(uuid.uuid4())
            list_ids.append(p_id)
            places.append(
                Place(place=p_id, province=prov_id, clasification="school"))

        schools[PRE_UNIVERSITY_SCHOOL] = list_ids
        list_ids = []
        for _ in range(university_schools_len):
            p_id = str(uuid.uuid4())
            list_ids.append(p_id)
            places.append(
                Place(place=p_id, province=prov_id, clasification="school"))

        schools[UNIVERSITY_SCHOOL] = list_ids

        # the neighborhoods are created
        possible_people_by_household = np.arange(start=1, stop=10, step=1)
        inhabitants_distribution = np.array(
            self.data_source.inhabitants_distribution)
        total_households_by_neighborhoods = int(
            700 / (np.argmax(inhabitants_distribution)+1))
        people_number_by_household = np.random.choice(a=possible_people_by_household,
                                                      p=inhabitants_distribution,
                                                      size=(total_neighborhoods, total_households_by_neighborhoods))
        # total_people = sum(people_number_by_household[i])
        #       for i in range(people_number_by_household.shape[0])])
        # Create household list from people_number_by_household
        households = []
        for i in range(people_number_by_household.shape[0]):
            neigh_id = uuid.uuid4()
            places.append(Place(place=str(neigh_id),
                          province=prov_id, clasification="neighborhood"))
            for j in range(people_number_by_household.shape[1]):
                h_id = uuid.uuid4()
                places.append(
                    Place(place=str(h_id), province=prov_id, clasification="house"))
                households.append({'id': str(
                    h_id), 'number_of_people': people_number_by_household[i][j], 'neighborhood_id': str(neigh_id)})

        start_time = timer()
        for h in households:
            # with Pool(30) as p:
            # p.apply_async(create_people_by_household,
            #               args=(prov_id, self.data_source, h, schools))
            self.create_people_by_household(
                prov_id, self.data_source, h, schools)

            # person_list.append(str(i.id))

        del households
        del schools

        print('Finished people in ', timer() - start_time)

        start_time = timer()

        # people_that_work = list(self.db.find(
        #     Person, Person.work == True))

        assert self.people_that_work is not None
        assert len(self.people_that_work) is not None
        print(len(self.people_that_work))
        people_that_work = self.assign_workplaces_to_people(
            province, prov_id, len(self.people_that_work), self.people_that_work)

        self.db.save_all(self.people_that_work)
        self.db.save_all(places)

        print('Finished workers in ', timer() - start_time)

        if verbose >= 2:
            print("Finished:", province)

    def assign_workplaces_to_people(self, province: str, prov_id: str, total_workers: int, people_that_works: list[Person]):

        workers_count = 0
        workplace_size_by_people = np.random.choice(
            a=[0, 1, 2, 3], size=len(people_that_works))

        people_mask = np.zeros(len(people_that_works))
        workplaces = []
        places = []
        while workers_count < total_workers:
            size = np.random.choice(a=[0, 1, 2, 3], size=1)[0]
            wp = str(uuid.uuid4())
            places.append(
                Place(place=wp, province=prov_id, clasification='work'))
            wp_current_workers = 0
            for i in range(len(people_that_works)):
                if people_mask[i] == 0 and workplace_size_by_people[i] == size:
                    people_that_works[i].workplace = wp
                    # workplaces.append(wp)
                    people_mask[i] = 1
                    workers_count += 1
                    wp_current_workers += 1
                    if wp_current_workers == size:
                        break

        self.db.save_all(places)
        return people_that_works

    def run_simulation(self, population_name: str, n_days: int = 2, n_processes=12):
        """Code to run simulation, it gets the contacts based on some pre-stablished rules

        Args:
            population_name (str): name of the population to simulate, it will load the simulation from DB
            n_days (int, optional): number of days to simmulate, the more days more accurate should be. Defaults to 2.
            n_processes (int, optional): number of processes to concurrenlty run. Defaults to 12.
        """
        start_time = timer()
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
                print(i)
                for time in ['morning', 'noon', 'afternoon', 'night']:

                    for prov in provinces:
                        prov_id = provinces[prov]
                        province = self.db.find(
                            Person, Person.province == prov_id)
                        for person in province:
                            assert person != None, 'Person cant be None'
                            place = move_person(
                                person, i, time, self.politics_deployed, self.db)
                            # pers = person.__dict__
                            # pers['id'] = str(person.id)
                            # # print(str(person.id))
                            # person_obj = SimP.load_serialized(pers)
                            # place = person_obj.move(
                            #     i, time, self.politics_deployed)

                            person.current_place = place

                            action = Action(destination=person.current_place, person=person.id,
                                            day=i, time=time, simulation_id=1)
                            self.db.save(action)
                            self.db.save(person)

            print("Implementing contact reduction politics")

            politics = {
                "close_shcools": {"school": 0},
                "mid_shcools": {"school": 0.5},
                "reduce_movility": {"neighborhood": 0.6, "random_place": 0.3},
                "close_workplaces": {"workplace": 0.1},
                "social_awareness": {key: 0.2 for key in self.politics_deployed.keys()}
            }

            print(f"Finished in {timer() - start_time}")
            # apply_politics(politics)

    def generate_contact_matrix(self, population_name: str, n_days: int):

        population = self.db.find_one(
            Population, Population.name == population_name)

        for province in population.provinces:
            for day in range(1, n_days+1):
                print(day)
                for time in ['morning', 'noon', 'afternoon', 'night']:
                    for place in db.find(Place, Place.province == population.provinces[province]):
                        actions = self.db.find(
                            Action, Action.destination == place.place, Action.day == day, Action.time == time)
                        people = [act.person for act in actions]
                        if len(people) == 0:
                            continue
                        # print(people)
                        interacted = np.random.choice(
                            people, np.random.poisson(lam=(len(people)/3)))

                        for p_id in interacted:

                            person = self.db.find_one(
                                Person, Person.id == ObjectId(p_id))

                            if not person:
                                continue

                            person.interacted.extend(
                                list(zip(interacted, [place.clasification] * len(interacted))))

                            if time == 'night':
                                self.add_contacts_to_matrix(
                                    person.interacted, person.age_group)
                                person.interacted = []

                            # print(person)
                            self.db.save(person)

        return self.mat

    def add_contacts_to_matrix(self, interacted, age_group):

        for p_id, place in interacted:

            person = self.db.find_one(Person, Person.id == ObjectId(p_id))

            self.mat[place][age_group][person.age_group] += 1
            self.mat[place][person.age_group][age_group] += 1
