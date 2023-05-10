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

    def __init__(self, province: str, school_type: str):
        """
        Args:
            province (str): the province name
            school_type (str): the school type
        """
        self.province = province
        self.school_type = school_type
        self.students = []
