# from data_distribution import prob_density
import numpy as np
from data_loader import DataLoader


class Household:
    """Class that represents a Household in the world

    Attributes:
    -----------
    number_of_persons (int):
        an int between 1 and 9, randomly generated on instanciation, represents the number of
        people in the house
    persons (list[Person]):
        a list containing the instances of Person for the house inhabitants
    province (str):
        a string with the province name
    neighborhood (int):
        an int with the neighborhood number, to identify locality

    """

    def __init__(self, province: str, neighborhood: int, data_source: DataLoader):
        """

        Args:
            province (str): province name
            neighborhood (int): neighborhood ID
        """

        # according to household size probability in data_distribution
        # a number of inhabitants is generated
        # min val: 1, max val: 9
        self.number_of_persons = np.random.choice(
            9, 1, p=data_source.inhabitants_distribution)[0]+1

        # initially persons list is empty, on World creation, the inhabitants will be added
        self.persons = []

        self.province = province
        self.neighborhood = neighborhood
