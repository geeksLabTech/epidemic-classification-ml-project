from typing import Dict, Any, List
from simulation import Person


class School:
    """Class that represents Schools

    Attributes:
    -----------
    province (str):
        a string with the name of the province, for more detailed matrices
    school_tipe (str):
        a formatted string with one of the posible values ('primary','secondary','pre_univ','university')
    students (list[Person]):
        a list of instances of Person, with all the students in the school
    """

    def __init__(self, province: str, school_type: str, students: list = []):
        """
        Args:
            province (str): the province name
            school_type (str): the school type
        """
        self.province = province
        self.school_type = school_type
        self.students = students

    def serialize(self) -> str:
        data = {
            "province": self.province,
            "school_type": self.school_type,
            "students": self.students
        }
        return data

    @classmethod
    def load_serialized(cls, data: Dict[str, Any]) -> "School":
        province = data["province"]
        school_type = data["school_type"]
        school = cls(province, school_type)
        school.students = data['students']
        return school
