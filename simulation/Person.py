import numpy as np
from data_loader import DataLoader
from models.action import Action
from models.person import Person as PersonModel
from odmantic import SyncEngine, Model
from pymongo import MongoClient


def get_random_element_from_collection():
    # Replace with your MongoDB connection string
    client = MongoClient("mongodb://localhost:27017")
    db = client["contact_simulation"]  # Replace with your database name
    # Replace with your collection name
    collection = db["person"]

    # Get the count of documents in the collection
    count = collection.count_documents({})
    flag = True

    while flag:
        # Generate a random index within the range of the document count
        random_index = np.random.randint(0, count - 1)

        # Get the random element
        random_element = list(collection.find().skip(random_index).limit(1))

        # Create a Person instance from the retrieved document
        random_p = random_element[0]
        # print(random_p)
        try:
            person = Person.load_serialized(random_p)
            flag = False
        except KeyError:
            pass

    client.close()

    return person


class Person:
    """Class representing a Person, the core of the simulation.

        Attributes:
        -----------
        id (str):
            unique identifier for the Person instance
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
        study_details_id (str):
            unique identifier of the referenced StudyDetails instance
        economic_activity_id (str):
            unique identifier of the referenced EconomicActivity instance
    """

    def __init__(self, data_source: DataLoader = DataLoader(), is_adult_required: bool = False):
        """Person generation takes all demographic data to fill needed fields
            Attributes:
            ----------
            data_source (DataLoader):
                DataLoader instance that has all the data required and formatted
            id (str):
                unique identifier for the Person instance
        """

        self.id = id
        self.current_location = None

        # age_group is assigned according to the distibution
        # age_group is assigned according to the distibution
        if is_adult_required:
            adult_groups_idx = np.arange(
                start=4, stop=len(data_source.age_groups))
            adult_groups_distribution = data_source.distribution_by_age_groups[4:]
            # self.age_group = np.random.choice(a=adult_groups_idx, p=adult_groups_distribution, size=1)
            self.age_group = np.random.choice(a=adult_groups_idx, size=1)[0]
        else:
            self.age_group = np.random.choice(
                a=14, size=1, p=data_source.distribution_by_age_groups)[0]

        # once the age group is selected, an uniform distribution is assumed
        # for all ages within the age range on the age group
        # age is then selected
        # print('group', self.age_group)
        start_age, stop_age = data_source.age_groups[self.age_group]
        possible_ages = np.arange(start=start_age, stop=stop_age, step=1)
        self.age = np.random.choice(a=possible_ages, size=1)

        # sex is also selected using the probabilities in data_distribution
        self.sex = bool(np.random.choice(
            2, 1, p=data_source.distribution_of_man_or_woman)[0])
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
            if np.random.random() < data_source.enrollment_distribution[2]/data_source.total_enrrollment:
                self.study_details = 'pre_univ'
                self.study = True

        # for university, in case of a person being over 30 years
        # the probability of studying is gradually reduced
        elif self.age > 18:
            population_coef = data_source.total_enrrollment
            if self.age > 30:
                population_coef *= self.age/10
            if np.random.random() < data_source.enrollment_distribution[3]/population_coef:
                self.study_details = 'university'
                self.study = True

        # if the person if older than 15, according to its sex
        # and the distribution, its determined wether or not it
        # is an active worker
        if self.age > 15 and self.age < 75:
            if self.sex:
                active = np.random.choice(
                    2, 1, p=data_source.active_woman_in_working_age)
            else:
                active = np.random.choice(
                    2, 1, p=data_source.active_man_in_working_age)

            if active:
                self.work = True

                # select corresponding distribution given sex
                if not self.sex:
                    act = data_source.man_distribution_by_economic_activity
                else:
                    act = data_source.woman_distribution_by_economic_activity
                # economic activity is selected
                self.economic_activity = np.random.choice(16, 1, act)[0]

    def move(self, db_obj, day, time, politics_deployed, sim_id: str, db=SyncEngine(database='contact_simulation')):
        probabilities = {
            "morning": {"household": 4, "workplace": 45, "neighborhood": 1, "random place": 5},
            "noon": {"household": 2, "workplace": 65, "neighborhood": 1, "random place": 5},
            "afternoon": {"household": 45, "workplace": 1, "neighborhood": 3, "random place": 15},
            "night": {"household": 6, "workplace": 5, "neighborhood": 2, "random place": 15}
        }

        probabilities_adjusted = probabilities.get(time, {})
        for i in probabilities_adjusted:
            probabilities_adjusted[i] *= politics_deployed[i]
        # print(probabilities_adjusted)

        if not self.work:
            probabilities_adjusted['workplace'] = 0

        if self.study:
            probabilities_adjusted["school"] = 0.6
            probabilities_adjusted["workplace"] = 0

        total_probability = sum(probabilities_adjusted.values())

        if total_probability <= 0:
            print("No available places to move.")
            return

        probabilities = list(probabilities_adjusted.values()) / \
            np.linalg.norm(list(probabilities_adjusted.values()), ord=1)

        choices = list(probabilities_adjusted.keys())

        next_location = np.random.choice(choices, p=probabilities)
        # print(probabilities)
        if next_location == 'random place':
            while True:
                random_person = get_random_element_from_collection()
                places = [
                    random_person.household,
                    random_person.school,
                    random_person.neighborhood,
                    random_person.workplace
                ]
                places = [i for i in places if i != None]
                if len(places) > 0:
                    break
            place_id = np.random.choice(a=places)
            self.current_location = place_id

            # print(f"moved to random place: {place_id}")
        elif self.current_location == self.__dict__[next_location]:
            pass
            # print(f"decided not to move, stayed at {self.current_location}")
        else:
            self.current_location = self.__dict__[next_location]

            # print("Moved to", next_location)

        db_obj.current_place = self.current_location
        db.save(db_obj)

        action = Action(destination=self.current_location, person=str(self.p_id),
                        day=day, time=time, simulation_id=sim_id)
        db.save(action)

    def serialize(self):
        serialized = {
            "age_group": int(self.age_group),
            "age": int(self.age),
            "sex": self.sex,
            "work": self.work,
            "study": self.study,
        }
        if self.study:
            serialized["study_details"] = self.study_details
        if self.work:
            serialized["economic_activity"] = int(self.economic_activity)
        # print(serialized)
        return serialized

    @ staticmethod
    def load_serialized(serialized):
        person = Person()
        person.age_group = serialized["age_group"]
        person.age = serialized["age"]
        person.sex = serialized["sex"]
        person.work = serialized["work"]
        person.study = serialized["study"]
        person.study_details = serialized["study_details"]
        person.economic_activity = serialized["economic_activity"]
        person.workplace = serialized['workplace']
        person.current_location = serialized['current_place']
        person.school = serialized['school']
        person.neighborhood = serialized['neighborhood']
        person.household = serialized['household']

        try:
            person.p_id = serialized['id']
        except KeyError:
            person.p_id = serialized['_id']

        return person
