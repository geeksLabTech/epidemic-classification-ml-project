import pandas as pd
import numpy as np
from models.contact_matrix import ContactMatrix
from odmantic import SyncEngine
from sklearn.model_selection import train_test_split
import json

db = SyncEngine(database='contact_simulation')
matrix = db.find(ContactMatrix)
for i in matrix:
    item = {"vector": i.vector, "matrix": i.data}

    with open("dataset.json", 'a') as f:
        json.dump(item, f)
        f.write("\n")
