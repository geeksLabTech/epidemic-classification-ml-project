

from enum import Enum
from beanie import Document
from odmantic import Model



class School(Model):
    province: str
    school_type: str


