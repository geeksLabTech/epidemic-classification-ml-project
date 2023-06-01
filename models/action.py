from odmantic import Model, ObjectId


class Action(Model):
    destination: str
    person: ObjectId
    day: int
    time: str
    simulation_id: str
