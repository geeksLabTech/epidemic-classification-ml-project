
from odmantic import Model 

class ContactMatrix(Model):
    category: str 
    # Integer that represent in which iteration was the matrix builded
    iteration: int
    data: list[list[float]]
    # This is for allow storing matrices of different simulation styles
    simulation_type: str

