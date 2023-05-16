# from data_distribution import prob_density
import numpy as np
from data_loader import DataLoader


import json


class Household:
    """Class that represents a Household in the world

    Attributes:
    -----------
    number_of_persons (int):
        an int between 1 and 9, randomly generated on instanciation, represents the number of
        people in the house
    persons (list[int]):
        a list containing the IDs of the Person instances for the house inhabitants
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
            h_id (int): unique identifier for house in given province
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

    def add_person(self, person_id: int):
        """Add a Person instance to the household

        Args:
            person_id (int): ID of the Person instance to add to the household
        """
        self.persons.append(person_id)

    def serialize(self):
        """Serialize the Household instance
        """

        return {
            'number_of_persons': int(self.number_of_persons),
            'persons': self.persons,
            'province': self.province,
            'neighborhood': int(self.neighborhood)
        }

    @classmethod
    def load_serialized(cls, data, data_source: DataLoader):
        """Load a serialized Household instance

        Args:
            filename (str): name of the file containing the serialized data
            data_source (DataLoader): instance of DataLoader class to use for loading Person instances

        Returns:
            Household: deserialized Household instance
        """

        household = cls(
            data['province'], data['neighborhood'], data_source)
        household.number_of_persons = data['number_of_persons']
        household.persons = data['persons']
        return household
