

from enum import Enum

from odmantic import Model



class School(Model):
    province: str
    school_type: str


