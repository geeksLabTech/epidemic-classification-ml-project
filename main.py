from World import World
from data_loader import DataLoader
import datetime

with open("date.txt", "w") as f:
    f.write(str(datetime.datetime.now()))

dl = DataLoader()
w = World(dl)

w.generate_population("CUBA")
w.run_simulation("CUBA")
w.generate_contact_matrix("CUBA")

with open("date.txt", "a") as f:
    f.write(str(datetime.datetime.now()))
