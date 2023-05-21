from odmantic import Model
from typing import Dict
from models.household import Household
from models.workplace import Workplace
from models.school import School


class Province(Model):
    province: str
    households: list
    workplaces: list
    schools: Dict[str, list]
