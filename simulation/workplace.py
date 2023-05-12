

from enum import Enum

import numpy as np


class WorkplaceSize(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    EXTRA_LARGE = 4


class Workplace:
    def __init__(self, id: int, province: str, size: WorkplaceSize, number_of_people: int | None = None):
        self.id = id
        self.province = province
        self.size = size,
        # self.economic_activity = economic_activity
        self.number_of_people = number_of_people
        if number_of_people is None:
            self.__assign_people_by_size()


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



