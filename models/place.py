from odmantic import Model
from uuid import UUID, uuid4


class Place(Model):
    place: str
    province: str
