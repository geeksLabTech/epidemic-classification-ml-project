from odmantic import Model, ObjectId


class Action(Model):
    destination: str
    destination_id: ObjectId
    person: ObjectId
    day: int
    time: str
    simulation_id: str
