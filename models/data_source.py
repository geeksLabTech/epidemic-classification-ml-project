
from pydantic import BaseModel
import numpy as np
from uuid import uuid4


class DataSource(BaseModel):
    provinces_population: dict[str, int]
    total_employees: int
    total_population: int
    teacher_number: int
    active_man_in_total_population: list[float]
    active_people_in_working_age: list[float]
    working_age: list[float]
    active_man_in_working_age: list[float]
    active_woman_in_working_age: list[float]
    active_by_sex: list[float]
    proffesors_by_sex: list[float]
    primary_schools_per_thousand_people: float
    secondary_schools_per_thousand_people: float
    pre_universitary_schools_per_thousand_people: float
    universities_per_province: float
    distribution_by_economic_activity: list[float]
    woman_distribution_by_economic_activity: list[float]
    man_distribution_by_economic_activity: list[float]
    age_groups: list[list[int]]
    distribution_by_age_groups: list[float]
    distribution_of_man_or_woman: list[float]

    neighborhoods_per_thousand_people: float
    inhabitants_distribution: list[float]


class DataSourceFactory:

    def create_random_population(self):
        province = str(uuid4())

        total_population = np.random.randint(10000, 2000000)
        provinces_population = {province: total_population}

        total_employees = np.random.randint(
            total_population//2, total_population)
        teacher_number = np.random.randint(total_employees//2, total_employees)
        active_man_in_total_population = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(2), size=1)[0])

        # print('test', active_man_int_total_population)
        active_people_in_working_age = np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(2), size=1).tolist()[0]
        print('active', active_people_in_working_age)
        working_age = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(2), size=1)[0])
        active_man_in_working_age = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(2), size=1)[0])
        active_woman_in_working_age = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(2), size=1)[0])
        active_by_sex = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(2), size=1)[0])
        proffesors_by_sex = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(2), size=1)[0])
        primary_schools_per_thousand_people = np.random.randint(1, 10)
        secondary_schools_per_thousand_people = np.random.randint(1, 10)
        pre_universitary_schools_per_thousand_people = np.random.randint(1, 10)
        universities_per_province = np.random.randint(1, 3)
        distribution_by_economic_activity = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(16), size=1)[0])
        man_distribution_by_economic_activity = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(16), size=1)[0])
        woman_distribution_by_economic_activity = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(16), size=1)[0])
        age_groups = [[0, 4], [5, 9], [10, 14], [15, 19], [20, 24], [25, 29], [
            30, 34], [35, 39], [40, 44], [45, 49], [50, 54], [55, 59], [60, 64], [65, 100]]
        distribution_by_age_groups = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(len(age_groups)), size=len(age_groups))[0])
        distribution_of_man_or_woman = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(2), size=1)[0])
        neighborhoods_per_thousand_people = 1.0
        inhabitants_distribution = list(np.random.dirichlet(
            alpha=self.create_random_alphas_for_dirichlet(9), size=1)[0])
        return DataSource(provinces_population=provinces_population, total_population=total_population, total_employees=total_employees, teacher_number=teacher_number, active_man_in_total_population=active_man_in_total_population, active_people_in_working_age=active_people_in_working_age, working_age=working_age, active_man_in_working_age=active_man_in_working_age, active_woman_in_working_age=active_woman_in_working_age, active_by_sex=active_by_sex, proffesors_by_sex=proffesors_by_sex, primary_schools_per_thousand_people=primary_schools_per_thousand_people, secondary_schools_per_thousand_people=secondary_schools_per_thousand_people, pre_universitary_schools_per_thousand_people=pre_universitary_schools_per_thousand_people, universities_per_province=universities_per_province, distribution_by_economic_activity=distribution_by_economic_activity, man_distribution_by_economic_activity=man_distribution_by_economic_activity, woman_distribution_by_economic_activity=woman_distribution_by_economic_activity, distribution_by_age_groups=distribution_by_age_groups, age_groups=age_groups, distribution_of_man_or_woman=distribution_of_man_or_woman, neighborhoods_per_thousand_people=neighborhoods_per_thousand_people, inhabitants_distribution=inhabitants_distribution)

    def create_random_alphas_for_dirichlet(self, size):
        return np.random.choice(np.arange(start=1, stop=size+1, step=1), size=size)


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

    def vectorize_data(self):

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
    
