from sklearn.feature_extraction import DictVectorizer
import numpy as np
import json


class InvalidDataError(Exception):
    pass


class DataLoader:

    def __init__(self, file='data.json'):

        with open(file) as f:
            data = json.loads(f.read())

        required_fields = [
            'total_population',
            'distribution_by_age_groups',
            'distribution_of_man_or_woman',
            'enrollment_distribution',
            'active_woman_in_working_age',
            'active_man_in_working_age',
            'man_distribution_by_economic_activity',
            'woman_distribution_by_economic_activity',
            'age_groups',
            'total_enrollment',
            'provinces_population',
            'neighborhoods_per_thousand_people',
            'primary_schools_per_thousand_people',
            'secondary_schools_per_thousand_people',
            'pre_universitary_schools_per_thousand_people',
            'universities_per_province',
            'provinces_population',
            'inhabitants_distribution'
        ]

        missing = []
        for i in required_fields:
            if not i in data:
                missing.append(i)
        if len(missing) > 0:
            raise InvalidDataError(
                f"Provided JSON is invalid, fields {missing} were expected but not found")

        self.total_population = data['total_population']
        self.total_enrollment = data['total_enrollment']

        self.distribution_by_age_groups = data['distribution_by_age_groups']
        self.age_groups = data['age_groups']
        self.distribution_of_man_or_woman = data['distribution_of_man_or_woman']

        self.enrollment_distribution = data['enrollment_distribution']

        self.active_people_in_working_age = data['active_people_in_working_age']
        self.active_man_in_working_age = data['active_man_in_working_age']
        self.active_woman_in_working_age = data['active_woman_in_working_age']
        self.man_distribution_by_economic_activity = data['man_distribution_by_economic_activity']
        self.woman_distribution_by_economic_activity = data['woman_distribution_by_economic_activity']

        self.provinces_population = data['provinces_population']
        self.neighborhoods_per_thousand_people = data['neighborhoods_per_thousand_people']

        self.primary_schools_per_thousand_people = data['primary_schools_per_thousand_people']
        self.secondary_schools_per_thousand_people = data['secondary_schools_per_thousand_people']
        self.pre_universitary_schools_per_thousand_people = data[
            'pre_universitary_schools_per_thousand_people']
        self.universities_per_province = data['universities_per_province']

        self.provinces_population = data['provinces_population']
        self.inhabitants_distribution = data['inhabitants_distribution']

    def _make_vector(self, dt):
        data = []

        if type(dt) == type([]):
            for i in dt:
                data.extend(self._make_vector(i))
        elif type(dt) == type({}):
            for key in dt:
                data.extend(_make_vector(dt[key]))
        else:
            return [dt]

        return data

    def vectorize_data(self,):

        data = self.__dict__
        print(data)

        data_to_append = []

        final_dict = {}

        for key in data.keys():
            if key == 'provinces_population':
                continue

            if type(data[key]) is type(list()):
                data_to_append.extend(self._make_vector(data[key]))
            elif type(data[key]) == type({}):
                data_to_append.extend(self._make_vector(data[key]))
            else:
                final_dict[key] = data[key]
        v = DictVectorizer(sparse=False)
        X = v.fit_transform(final_dict)

        X = np.append(X[0], data_to_append, axis=0)

        print(X)

        return X
