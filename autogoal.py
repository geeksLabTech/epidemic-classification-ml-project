from autogoal.ml import AutoML
from autogoal.kb import Vector, Matrix, Supervised
from autogoal.search import RichLogger
from data_loader import DataLoader
import pandas as pd
import numpy as np


automl = AutoML(
    input=(Vector, Supervised[Vector]),
    output=Matrix, )

automl.fit(X_train, y_train, logger=RichLogger())

best_pipeline = automl.best_pipeline_(X_train, y_train)
best_score = automl.best_score_(X_test, y_test)
