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

    def __init__(self):
        """initialization function
        """
        self.total_population = 0
        self.db = MongoCRUD('contact_simulation')

    def generate_population(self, population_name: str, data_source: DataLoader, n_threads: int = 12):
        self.data_source = data_source
        self.person_id = 1
        self.house_id = 1
        self.neighborhood_id = 1

        provinces = []

        for i in data_source.provinces_population:
            provinces.append(self.generate_province(i, n_threads=n_threads))

        self.db.insert_data("Population", {"population_name": population_name,
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

        workplaces = []
        # workplaces: dict[str, list[Workplace]] = {}
        # according to distribution, the province population is divided by
        # the number of people per neighborhood
        # resulting on the number of neighborhoods in the province
        total_neighborhoods = int(
            self.data_source.provinces_population[province]/(self.data_source.neighborhoods_per_thousand_people*1000))+1

        if verbose >= 2:
            print(province)

        # schools in province are organized according to school type
        schools = {
            'primary': [],
            'secondary': [],
            'pre_univ': [],
            'university': []
        }

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

        # for each type of school's number of schools
        # a school is created and stored
        for sc_tp in num_of_schools.keys():
            print(sc_tp)
            # for _ in range(int(num_of_schools[sc_tp])):
            # self.build_school((sc_tp, province))
            print(int(num_of_schools[sc_tp]))
            with Pool(n_threads) as p:
                schools[sc_tp] = p.map(self.build_school, [
                                      (sc_tp, province) for i in range(int(num_of_schools[sc_tp]))])

        print(f"Building {total_neighborhoods}")
        neighborhoods = []
        # the neighborhoods are created
        neighborhoods_id = []
        # for i in range(total_neighborhoods):
        #     neighborhoods_id.append(
        #         self.build_neighborhood((i, province, schools)))
        with Pool(n_threads) as p:
            neighborhoods_id = p.map(self.build_neighborhood, [
                (i, province, schools) for i in range(total_neighborhoods)])
        neighborhoods.append(neighborhoods_id)
        # self.neighborhood_id += 1

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
        prov_id = self.db.insert_data("Province", {
            province: {
                "neighborhoods": neighborhoods,
                "schools": schools,
                "workplaces": workplaces
            }
        }).inserted_id

        if verbose >= 2:
            print("Finished:", province)
        with open("date.txt", 'a') as f:
            f.write(province)
            f.write(str(datetime.datetime.now()))

        return prov_id

    def build_neighborhood(self, data):
        n_id, province, schools = data
        cont = 0
        neighborhood = []
        # cont denotes the number of persons in the current neighborhood
        # while its less than the number of persons per neghborhood
        while cont < self.data_source.neighborhoods_per_thousand_people * 1000:
            # print(
            #     cont, "/", self.data_source.neighborhoods_per_thousand_people * 1000)
            # a household is created
            h = Household(province, n_id, self.house_id, self.data_source)
            self.house_id += 1
            cont += h.number_of_persons
            has_elder = False
            self.total_population += h.number_of_persons
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
                    sc = None
                    if p.study:
                        sc = np.random.choice(schools[p.study_details])

                    id = self.db.insert_data(
                        "Person", p.serialize()).inserted_id
                    if sc:
                        self.db.update_one(
                            "School", {"_id": sc}, 'students', id)
                        # school = self.db.get_data(
                        #     "School", filter_query={"_id": sc})
                        # print(school)
                        # school['students'].append(id)

                    h.persons.append(id)
                    del p
            neighborhood.append(h.serialize())
            del h
        n_id = self.db.insert_data(
            "Neighborhood", {"neighborhood": neighborhood}).inserted_id
        return n_id

    def build_school(self, data):
        sc_tp, province = data
        school = {
            "province": province,
            "school_type": sc_tp,
            "students": []}
        return self.db.insert_data(
            "School", school).inserted_id
        # del school

    def run_simulation(self, population_name: str, n_days: int = 100):
        population: dict = self.db.get_data(
            "Population", {"population_name": population_name})

        if population:
            provinces = population['provinces']

            # each day will be divided in 3 possible contact moments
            # 1: At Work/School (contacts related to the workplace and school representing the day for the people in the population)
            # 2: In the neighborhood (contacts in the neighborhood, in this step is assumed contact between friends)
            # 3: In House conttacts (family members)
            for day in range(1, n_days):

                # TODO: extract this to paralelize
                for province in provinces:
                    # TODO: to be implemented
                    for workplace in province['workplaces']:
                        pass

                    for sc_tp in province['schools']:
                        for school in sc_tp:
                            sc_obj = School.load_serialized(
                                self.db.get_data("School", {"_id": school}))

                            pairs = self.generate_contacts(sc_obj.students, 40)
                            self.insert_pairs(pairs,  population_name,
                                              str(sc_tp)+' school')

                    # geenrate contacts in house and store all persons to
                    # generate neighborhood contacts
                    for n_id in province['neighborhoods']:
                        neighborhood = self.db.get_data(
                            'Neighborhood', {"_id": n_id})

                        persons = []

                        for house in neighborhood:
                            persons.append(house['persons'])
                            pairs = self.generate_contacts(
                                house['persons'], house["n_persons"])

                            self.insert_pairs(
                                day, pairs, population_name, "home")

                        pairs = self.generate_contacts(
                            persons, np.random.randint(5, 30))
                        self.insert_pairs(
                            day, pairs, population_name, "neighborhood")

    def generate_contacts(self, arr: list, n_contacts: int):  # -> list(tuple(int,int))
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

        return pairs

    def insert_pairs(self, day, pairs, population, place):
        for p in pairs:
            p1, p2 = self.db.get_data("People", {"_id": p[0]}), self.db.get_data(
                "People", {"_id": p[0]}),

            contact = {
                "day": day
                "population": population,
                "place": place,
                "p1": p1['age'],
                "p2": p2['age']
            }

            self.db.insert_data("Contact", contact)
