from sklearn.feature_extraction import DictVectorizer
import json
import numpy as np


def make_vector(dt):
    data = []

    if type(dt) == type([]):
        for i in dt:
            data.extend(make_vector(i))
    elif type(dt) == type({}):
        for key in dt:
            data.extend(make_vector(dt[key]))
    else:
        return [dt]

    return data


def vetorize_data(fp='data.json'):

    with open(fp) as f:
        data = json.load(f)

    data_to_append = []

    final_dict = {}

    for key in data.keys():
        if type(data[key]) is type(list()):
            data_to_append.extend(make_vector(data[key]))
        elif type(data[key]) == type({}):
            if key == 'provinces_population':
                break
            data_to_append.extend(make_vector(data[key]))
        else:
            final_dict[key] = data[key]
    v = DictVectorizer(sparse=False)
    X = v.fit_transform(final_dict)

    X = np.append(X[0], data_to_append, axis=0)

    print(X)

    return X


vetorize_data()
