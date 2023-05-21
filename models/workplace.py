

from enum import Enum
from odmantic import Model
import numpy as np


# class WorkplaceSize(Enum):
#     SMALL = 1
#     MEDIUM = 2
#     LARGE = 3
#     EXTRA_LARGE = 4
#     NULL = 5


class Workplace(Model):
    province: str
    size: int
    number_of_people: int


class WorkplaceFactory:
    @classmethod
    def create(cls, province: str, size: int) -> Workplace:
        match size:
            case 0:
                number_of_people = np.random.randint(1, 10)
            case 1:
                number_of_people = np.random.randint(10, 50)
            case 2:
                number_of_people = np.random.randint(50, 200)
            case 3:
                number_of_people = np.random.randint(200, 1000)

        return Workplace(province=province, size=size, number_of_people=number_of_people)
        