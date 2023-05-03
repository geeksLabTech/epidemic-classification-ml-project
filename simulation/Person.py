import numpy as np
from data_distribution import *


class Person:
    def __init__(self):

        self.age_group = np.random.choice(
            14, 1, p=distribution_by_age_groups)[0]

        ages = [i for i in range(
            age_groups[self.age_group][0], age_groups[self.age_group][1])]

        self.age = np.random.choice(ages, 1)[0]
        self.sex = np.random.choice(2, 1, p=[
                                    distribution_of_woman_or_man[0], distribution_of_woman_or_man[1]+distribution_of_woman_or_man[2]])[0]
        self.work = self.study = False

        if self.age > 6 and self.age < 13:
            self.study = 'primary'
        # Enrollment and employment
        elif self.age <= 15:
            self.study = 'secondary`'
        # pre-universitary is assigned according to the distribution
        elif self.age > 15 and self.age < 18:
            if random.random() < enrollment_distribution[2]/total_population:
                self.study = 'pre_univ'
        # for university, in case of a person being over 30 years the probability is gradually reduced
        elif self.age > 18:
            population_coef = total_population
            if self.age > 30:
                population_coef *= self.age/10
            if random.random() < enrollment_distribution[3]/population_coef:
                self.study = 'university'

        if self.age > 15 and self.age < 75:
            self.work = True

            if self.sex == 0:
                act = man_distribution_by_activity_economic
            else:
                act = women_distribution_by_activity_economic

            self.economic_activity = np.random.choice(16, 1, act)
