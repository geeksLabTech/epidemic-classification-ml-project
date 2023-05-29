
from ast import Raise
from enum import Enum
from typing import Optional, Union
from odmantic import AIOEngine, Model, Reference, SyncEngine
from sklearn import neighbors
from models.data_source import DataSource
import numpy as np
from constants import PRIMARY_SCHOOL, SECONDARY_SCHOOL, PRE_UNIVERSITY_SCHOOL, UNIVERSITY_SCHOOL, NULL_SCHOOL, NULL_WORKPLACE

# class Sex(Enum):
#     Male = 0
#     Female = 1


class Person(Model):
    age_group: int
    age: int
    # 0 represents Male and 1 is Female
    sex: int
    work: bool
    study: bool
    study_details: Optional[str]
    household: str
    economic_activity: Optional[int]
    school: Optional[str]
    workplace: Optional[str]
    neighborhood: str
    last_place: str
    current_place: str
    province: str
    interacted: Optional[list]

def create_parallel(data) -> Person:
    data_source, household, schools, province = data
    return PersonFactory.create(data_source, household, schools, province)


def get_random_element_from_collection(db: SyncEngine):
    # Get the count of documents in the collection
    count = db.count(Person)
    if count == 0:
        raise RuntimeError('No people in collection')
    
    # flag = True

    # while flag:
        # Generate a random index within the range of the document count
    random_index = np.random.randint(0, count - 1)

    for p in db.find(Person, skip=random_index, limit=1):
        return p


    # return person


def move_person(person: Person, day, time, politics_deployed, db: SyncEngine):
        probabilities = {
            "morning": {"household": 4, "workplace": 45, "neighborhood": 1, "random place": 5},
            "noon": {"household": 2, "workplace": 65, "neighborhood": 1, "random place": 5},
            "afternoon": {"household": 45, "workplace": 1, "neighborhood": 3, "random place": 15},
            "night": {"household": 6, "workplace": 5, "neighborhood": 2, "random place": 15}
        }

        probabilities_adjusted = probabilities.get(time, {})
        for i in probabilities_adjusted:
            probabilities_adjusted[i] *= politics_deployed[i]
        # print(probabilities_adjusted)

        if not person.work:
            probabilities_adjusted['workplace'] = 0

        if person.study:
            probabilities_adjusted["school"] = 0.6
            probabilities_adjusted["workplace"] = 0

        total_probability = sum(probabilities_adjusted.values())

        if total_probability <= 0:
            print("No available places to move.")
            return

        probabilities = list(probabilities_adjusted.values()) / \
            np.linalg.norm(list(probabilities_adjusted.values()), ord=1)

        choices = list(probabilities_adjusted.keys())

        next_location = np.random.choice(choices, p=probabilities)
        # print(probabilities)
        if next_location == 'random place':
            while True:
                random_person = get_random_element_from_collection(db)
                places = [
                    random_person.household,
                    random_person.school,
                    random_person.neighborhood,
                    random_person.workplace
                ]
                places = [i for i in places if i != None]
                if len(places) > 0:
                    break
            place_id = np.random.choice(a=places)
            person.current_location = place_id

            # print(f"moved to random place: {place_id}")
            # here was person.__dict__[next_location]
        elif person.current_place == next_location:
            pass
            # print(f"decided not to move, stayed at {self.current_location}")
        else:
            person.current_place = next_location

            # print("Moved to", next_location)
        return person.current_place

class PersonFactory():
    @ classmethod
    def create(cls, data_source: DataSource, household: dict, schools: dict[str, list[str]], province: str, is_adult_required=False) -> Person:
        age_group=cls.get_age_group(data_source, is_adult_required)

        # once the age group is selected, an uniform distribution is assumed
        # for all ages within the age range on the age group
        # age is then selected
        # print('group', age_group)
        start_age, stop_age=data_source.age_groups[age_group]
        possible_ages=np.arange(start=start_age, stop=stop_age, step=1)
        age=np.random.choice(a=possible_ages, size=1)[0]

        # sex is also selected using the probabilities in data_distribution
        sex=np.random.choice(
            [0, 1], 1, p=data_source.distribution_of_man_or_woman)[0]

        work=study=False
        study, study_details=cls.get_study_details(data_source, age)
        work, economic_activity=cls.get_work_info(data_source, age, sex)
        school_index=None if not study else np.random.choice(
            a=len(schools[study_details]), size=1)[0]
        school=NULL_SCHOOL if school_index is None else schools[study_details][school_index]

        person=Person(age=age, age_group=age_group, sex=sex, work=work, study=study, study_details=study_details, economic_activity=economic_activity, school=school,
                        household=household['id'], workplace=NULL_WORKPLACE, neighborhood=str(household['neighborhood_id']), current_place=household['id'], last_place=household['id'], province=province, interacted=[])

        return person

    @ classmethod
    def get_age_group(cls, data_source: DataSource, is_adult_required=False) -> int:
        if is_adult_required:
            adult_groups_idx=np.arange(
                start=4, stop=len(data_source.age_groups))

            return np.random.choice(a=adult_groups_idx, size=1)[0]

        return np.random.choice(a=14, size=1, p=data_source.distribution_by_age_groups)[0]

    @ classmethod
    def get_study_details(cls, data_source: DataSource, age: int) -> tuple[bool, Optional[str]]:
        if age > 6 and age < 13:
            return True, PRIMARY_SCHOOL

        elif age <= 15:
            return True, SECONDARY_SCHOOL

        # pre-universitary is assigned according to the distribution
        elif age > 15 and age < 18:
            if np.random.random() < data_source.enrollment_distribution[2]/data_source.total_enrollment:
                return True, PRE_UNIVERSITY_SCHOOL

        # for university, in case of a person being over 30 years
        # the probability of studying is gradually reduced
        elif age > 18:
            population_coef=data_source.total_enrollment
            if age > 30:
                population_coef *= age/10
            if np.random.random() < data_source.enrollment_distribution[3]/population_coef:
                return True, UNIVERSITY_SCHOOL

        return False, None

    @ classmethod
    def get_work_info(cls, data_source: DataSource, age: int, sex: int) -> tuple[bool, Optional[int]]:
        if age < 16 or age > 85:
            return False, None

        active=np.random.choice(
            2, size=1, p=data_source.active_people_in_working_age)[0]
        if active == 1:
            return False, None

        work=True
        # select corresponding distribution given sex
        act=data_source.man_distribution_by_economic_activity if sex == 0 else data_source.woman_distribution_by_economic_activity
        economic_activity=np.random.choice(a=len(act), size=1, p=act)[0]
        return work, economic_activity
