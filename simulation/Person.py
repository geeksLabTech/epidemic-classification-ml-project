import numpy as np
from data_distribution import *


class Person:
    def __init__(self):

        self.age_group = np.random.choice(
            14, 1, p=distribution_by_age_groups)[0]

        ages = [i for i in range(
            age_groups[self.age_group][0], age_groups[self.age_group][1])]

        self.age = np.random.choice(ages, 1)[0]
        self.sex = np.random.choice(2, 1, p=distribution_of_woman_or_man)[0]
        self.work = self.study = False

        # Enrollment and employment
        if self.age <= 15:
            self.study = True
        # pre-universitary is assigned according to the distribution
        if self.age > 15 and self.age < 18:
            if random.random() < enrollment_distribution[2]/total_population:
                self.study = True
        # for university, in case of a person being over 30 years the probability is gradually reduced
        if self.age > 18:
            population_coef = total_population
            if self.age > 30:
                population_coef *= self.age/10
            if random.random() < enrollment_distribution[3]/population_coef:
                self.study = True

        if self.age > 15 and self.age < 75:
            self.work = True

        