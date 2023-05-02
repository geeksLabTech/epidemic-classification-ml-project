from data_distribution import prob_density
import numpy as np


class Household:
    def __init__(self, province, neighborhood):
        self.number_of_persons = np.random.choice(9, 1, p=prob_density)[0]+1

        self.persons = []
        self.province = province
        self.neighborhood = neighborhood
