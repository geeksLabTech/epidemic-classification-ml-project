from odmantic import Model
from models.province import Province


class Population(Model):
    name: str
    provinces: dict
