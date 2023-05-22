from odmantic import Model

class Population(Model):
    name: str
    provinces: dict
