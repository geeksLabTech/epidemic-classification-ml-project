from autogoal.ml import AutoML
from autogoal.kb import Vector,Matrix, Supervised
from autogoal.search import RichLogger

data = ... # Load your data here

X_train, y_train, X_test, y_test = data

automl = AutoML(
    input=(Matrix, Supervised[Matrix]),  
    output=Matrix, )

automl.fit(X_train, y_train, logger=RichLogger())

best_pipeline = automl.best_pipeline_(X_train, y_train)
best_score = automl.best_score_(X_test, y_test)


