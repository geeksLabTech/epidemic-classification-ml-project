
from models.school import School
from models.workplace import Workplace

NULL_WORKPLACE = Workplace(province='Null Workplace', size=-1, number_of_people=0)
NULL_SCHOOL = School(province='Null School', school_type='NUll')
PRIMARY_SCHOOL = 'Primary'
SECONDARY_SCHOOL = 'Secondary'
PRE_UNIVERSITY_SCHOOL = 'PreUniversity'
UNIVERSITY_SCHOOL = 'University'