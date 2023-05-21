
from enum import Enum
from typing import Optional, Union
from odmantic import AIOEngine, Model, Reference
from sklearn import neighbors
from models.data_source import DataSource
from models.household import Household
from uuid import UUID
from models.school import School
from models.workplace import Workplace, WorkplaceFactory

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
    last_place: Optional[str]
    current_place: Optional[str]
    province: str

class PersonFactory():
    @classmethod
    def create(cls, data_source: DataSource, household: Household, schools: dict[str, list[str]], province: str, is_adult_required = False) -> Person:
        age_group = cls.get_age_group(data_source, is_adult_required)

        # once the age group is selected, an uniform distribution is assumed
        # for all ages within the age range on the age group
        # age is then selected
        # print('group', age_group)
        start_age, stop_age = data_source.age_groups[age_group]
        possible_ages = np.arange(start=start_age, stop=stop_age, step=1)
        age = np.random.choice(a=possible_ages, size=1)[0]

        # sex is also selected using the probabilities in data_distribution
        sex = np.random.choice(
            [0,1], 1, p=data_source.distribution_of_man_or_woman)[0]
        
        work = study = False
        study, study_details = cls.get_study_details(data_source, age)
        work, economic_activity = cls.get_work_info(data_source, age, sex)
        school_index = None if not study else np.random.choice(a=len(schools[study_details]), size=1)[0]
        school = NULL_SCHOOL if school_index is None else schools[study_details][school_index]

        person = Person(age=age, age_group=age_group, sex=sex, work=work, study=study, study_details=study_details, economic_activity=economic_activity, school=school, household=str(household.id), workplace=NULL_WORKPLACE, neighborhood=str(household.neighborhood_id), current_place=str(household.id), last_place=str(household.id), province=province)
        # person = Person(age=age, age_group=age_group, sex=sex, work=work, study=study)
        return person

    @classmethod
    def get_age_group(cls, data_source: DataSource, is_adult_required = False) -> int:
        if is_adult_required:
            adult_groups_idx = np.arange(
                start=4, stop=len(data_source.age_groups))
            
            return np.random.choice(a=adult_groups_idx, size=1)[0]
        
        return np.random.choice(a=14, size=1, p=data_source.distribution_by_age_groups)[0]
    
    @classmethod
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
            population_coef = data_source.total_enrollment
            if age > 30:
                population_coef *= age/10
            if np.random.random() < data_source.enrollment_distribution[3]/population_coef:
                return True, UNIVERSITY_SCHOOL

        return False, None
    
    
    @classmethod
    def get_work_info(cls, data_source: DataSource, age: int, sex: int) -> tuple[bool, Optional[int]]:
        if age < 16 or age > 75:
            return False, None
        
        active = np.random.choice(2, size=1, p=data_source.active_man_in_working_age)[0]
        if active == 0:
            return False, None
        
        work = True
        # select corresponding distribution given sex
        act = data_source.man_distribution_by_economic_activity if sex == 0 else data_source.woman_distribution_by_economic_activity
        economic_activity = np.random.choice(a=len(act), size=1, p=act)[0]
        return work, economic_activity
    

