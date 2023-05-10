import numpy as np
from data_distribution import *


class Person:
    """Class representing a Person, the core of the simulation.

        Attributes:
        -----------
        age_group (int):
            one of the 14 age groups (< 5, 5-9, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39,40-44, 45-49, 50-54, 55-59,60-64,65>)
        age (int):
            integer representing actual age
        sex (bool):
            bool representing sex (False: male, True: female)
        work (bool):
            bool representing if the person works or not 
        study (bool):
            bool representing if a person studies or not
        study_details (str):
            string denoting school_type, it is assigned acording to age
        economic_activity (int):
            integer representing one of the 16 economic activities in distribution
    """

    def __init__(self):
        """Person generation takes all demographic data to fill needed fields
        """

        # age_group is assigned according to the distibution
        self.age_group = np.random.choice(
            14, 1, p=distribution_by_age_groups)[0]

        # once the age group is selected, an uniform distribution is assumed
        # for all ages within the age range on the age group
        # age is then selected
        ages = [i for i in range(
            age_groups[self.age_group][0], age_groups[self.age_group][1])]
        self.age = np.random.choice(ages, 1)[0]
        del ages

        # sex is also selected using the probabilities in data_distribution
        self.sex = bool(np.random.choice(2, 1, p=[
            distribution_of_woman_or_man[0], distribution_of_woman_or_man[1]+distribution_of_woman_or_man[2]])[0])

        # initially work and study are false
        # for people with 15 or less years
        # it is mandatory to go to corresponding school
        self.work = self.study = False
        if self.age > 6 and self.age < 13:
            self.study_details = 'primary'
            self.study = True
        elif self.age <= 15:
            self.study_details = 'secondary'
            self.study = True

        # pre-universitary is assigned according to the distribution
        elif self.age > 15 and self.age < 18:
            if random.random() < enrollment_distribution[2]/total_population:
                self.study_details = 'pre_univ'
                self.study = True

        # for university, in case of a person being over 30 years
        # the probability of studying is gradually reduced
        elif self.age > 18:
            population_coef = total_population
            if self.age > 30:
                population_coef *= self.age/10
            if random.random() < enrollment_distribution[3]/population_coef:
                self.study_details = 'university'
                self.study = True

        # if the person if older than 15, according to its sex
        # and the distribution, its determined wether or not it
        # is an active worker
        if self.age > 15 and self.age < 75:
            if self.sex:
                active = np.random.choice(2, 1, p=active_woman_in_working_age)
            else:
                active = np.random.choice(2, 1, p=active_man_in_working_age)

            if active:
                self.work = True

                # select corresponding distribution given sex
                if not self.sex:
                    act = man_distribution_by_activity_economic
                else:
                    act = women_distribution_by_activity_economic
                # economic activity is selected
                self.economic_activity = np.random.choice(16, 1, act)
