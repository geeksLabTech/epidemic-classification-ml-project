from autogoal.ml import AutoML
from autogoal.kb import Vector, Matrix, Supervised
from autogoal.search import RichLogger
from sklearn.model_selection import train_test_split
import json
import pandas as pd
import numpy as np

with open('../dataset.json') as f:
    data = json.load(f)

X = []
Y = []

for i in data:
    X.append(i['vector'])
    Y.append(np.array(i['matrix']).flatten())

X_train, X_test, y_train, y_test = train_test_split(
    X, Y, test_size=None, train_size=None, random_state=None, shuffle=True, stratify=None)

automl = AutoML(
    input=(Vector, Supervised[Vector]),
    output=Vector, )

automl.fit(X_train, y_train, logger=RichLogger())

best_pipeline = automl.best_pipeline_(X_train, y_train)
best_score = automl.best_score_(X_test, y_test)
