from autogoal.ml import AutoML
from autogoal.kb import Vector, Matrix, Supervised
from autogoal.search import RichLogger
# from data_loader import DataLoader
import pandas as pd
import numpy as np
from models.contact_matrix import ContactMatrix
from odmantic import SyncEngine
from sklearn.model_selection import train_test_split


db = SyncEngine(database='contact_simulation')
X = []
Y = []
matrix = db.find(ContactMatrix)
for i in matrix:
    X.append(i.vector)
    Y.append(i.data)

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size= None,train_size=None, random_state=None, shuffle=True, stratify=None)
automl = AutoML(
    input=(Vector, Supervised[Vector]),
    output=Matrix, )

automl.fit(X_train, y_train, logger=RichLogger())

best_pipeline = automl.best_pipeline_(X_train, y_train)
best_score = automl.best_score_(X_test, y_test)
