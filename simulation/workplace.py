

from enum import Enum
from typing import List
import numpy as np


class WorkplaceSize(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    EXTRA_LARGE = 4


class Workplace:
    def __init__(self, province: str, size: WorkplaceSize, people_ids: List):
        self.province = province
        self.size = size
        self.people_ids = people_ids

    def serialize(self):
        """serialize object

        Returns:
            dict: dictionary with the serialized representation of self
        """
        return {
            'province': self.province,
            'size': str(self.size),
            'people_ids': self.people_ids
        }

    def __assign_people_by_size(self):
        match self.size:
            case WorkplaceSize.SMALL:
                self.number_of_people = np.random.randint(1, 10)
            case WorkplaceSize.MEDIUM:
                self.number_of_people = np.random.randint(10, 50)
            case WorkplaceSize.LARGE:
                self.number_of_people = np.random.randint(50, 200)
            case WorkplaceSize.EXTRA_LARGE:
                self.number_of_people = np.random.randint(200, 1000)
