from pydantic import BaseModel
from uuid import UUID, uuid4


class Household(BaseModel):
    id: UUID
    province: str
    number_of_people: int
    neighborhood_id: UUID

class HouseholdFactory:
    @classmethod
    def create(cls, neighborhood_id: UUID, province: str, number_of_people: int):
        return Household(id=uuid4(), province=province, number_of_people=number_of_people, neighborhood_id=neighborhood_id)