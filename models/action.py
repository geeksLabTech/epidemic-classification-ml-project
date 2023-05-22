from odmantic import Model, ObjectId


class Action(Model):
    destination: str
    person: str
    day: int
    time: str
    simulation_id: str
