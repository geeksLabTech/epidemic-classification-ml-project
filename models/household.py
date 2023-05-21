from odmantic import Model


class Household(Model):
    province: str
    number_of_people: int
