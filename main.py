from World import World
from data_loader import DataLoader
import datetime
import pandas as pd

# with open("date.txt", "w") as f:
#     f.write(str(datetime.datetime.now()))

dl = DataLoader()
w = World(dl)

print("Generating Population")
w.generate_population("CUBA", n_threads=100)
print("Done!, Simmulating days now...")
w.run_simulation("CUBA", 100)
print("Building Matrix")
labels = [str(i[0])+"-"+str(i[1]) for i in dl.age_groups]
# print(labels)
m = w.generate_contact_matrix("CUBA")
df = pd.DataFrame(m, columns=labels)

df.to_csv("matrix.csv")
# with open("date.txt", "a") as f:
#     f.write(str(datetime.datetime.now()))
