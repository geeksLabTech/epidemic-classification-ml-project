
from pydantic import BaseModel


class DataSource(BaseModel):
    provinces_population: dict[str,int]
    total_employees: int
    total_population: int
    teacher_number: int
    active_man_in_total_population: list[float]
    active_people_in_working_age: list[float]
    working_age: list[float]
    active_man_in_working_age: list[float]
    active_woman_in_working_age: list[float]
    active_by_sex: list[float]
    professors_by_sex: list[float]
    primary_schools_per_thousand_people: float
    secondary_schools_per_thousand_people: float
    pre_universitary_schools_per_thousand_people: float
    universities_per_province: float
    distribution_by_economic_activity: list[float]
    woman_distribution_by_economic_activity: list[float]
    man_distribution_by_economic_activity: list[float]
    age_groups: list[list[int]]
    distribution_by_age_groups: list[float]
    distribution_of_man_or_woman: list[float]
    enrollment_distribution: list[float]
    total_enrollment: int
    total_houses: int
    urban_rural: list[int]
    neighborhoods_per_thousand_people: float
    inhabitants_distribution: list[float]
