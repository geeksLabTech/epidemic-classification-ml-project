from simulation.Person import Person
from simulation.Household import Household
from simulation.School import School
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
            self.generate_province(i)

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
        workplaces = []
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
        # the neighborhoods are created
        neighborhoods_id = []
        # for i in range(total_neighborhoods):
        #     neighborhoods_id.append(
        #         self.build_neighborhood((i, province, schools)))
        with Pool(n_threads) as p:
            neighborhoods_id.append(p.map(self.build_neighborhood, [
                                    (i, province, schools) for i in range(total_neighborhoods)]))
        neighborhoods[province].append(neighborhoods_id)
        # self.neighborhood_id += 1

        self.db.insert_data("Province", {
            province: {
                "neighborhoods": neighborhoods[province],
                "schools": schools,
                "workplaces": workplaces
            }
        })

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
