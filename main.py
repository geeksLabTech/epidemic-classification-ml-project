from World import World
from data_loader import DataLoader
import datetime

with open("date.txt", "w") as f:
    f.write(str(datetime.datetime.now()))

dl = DataLoader()
w = World(dl, n_threads=12)

with open("date.txt", "a") as f:
    f.write(str(datetime.datetime.now()))
