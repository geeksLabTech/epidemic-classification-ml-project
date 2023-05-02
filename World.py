from simulation.Person import Person
from simulation.Household import Household
from data_distribution import *

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from multiprocessing import Pool


neighborhoods = []


def generate_neighborhoods(province):
    total_neighborhoods = int(provinces_population[province]/1000)+1
    print(province)
    for j in range(total_neighborhoods):
        cont = 0
        neighborhood = []

        while cont < 1000:
            h = Household(province, j)
            cont += h.number_of_persons
            for _ in range(h.number_of_persons):
                h.persons.append(Person())
            neighborhood.append(h)
        neighborhoods.append(neighborhood)
    print("Finished:", province)


# with ThreadPoolExecutor(max_workers=12) as executor:
    # for i in provinces_population:
with Pool(12) as p:
    results = []
    results.append(p.map(generate_neighborhoods, provinces_population))

print(neighborhoods)
