import random as random

provinces_population = {
    "Pinar del Rio": 583037,
    "Artemisa": 514332,
    "La Habana": 2132183,
    "Mayabeque": 384389,
    "Matanzas": 716320,
    "Villa Clara": 775091,
    "Cienfuegos": 406224,
    "Sancti Spiritus": 463844,
    "Ciego de Avila": 435326,
    "Camaguey": 763389,
    "Las Tunas": 533224,
    "Holguin": 1021591,
    "Granma": 817763,
    "Santiago de Cuba": 1045631,
    "Guantanamo": 505606,
    "Isla de la Juventud": 83625
}

# work-related distributions
total_employees = 47100
total_population = 11181595
teacher_number = 4817
# probability distribution of active persons with respect to the total population
# the first element represents the probability that they are active
active_man_in_total_population = [0.421, 0.579]
# probability distribution of active people of working age
# the first element represents the probability that are active
active_people_in_working_age = [0.663, 0.336]

# probability distribution of men and women of working age
# the first element represents the probability that they are male
working_age = [0.606, 0.394]

# distribution of the probability of being active if you are a woman
# the first element represents the probability that they are active
active_woman_in_working_age = [0.548, 0.452]

# distribution of the probability of being active if you are a man
# the first element represents the probability that they are active
active_man_in_working_age = [0.768, 0.232]

# probability distribution of assets by sex
# the first element represents the probability that they are male
active_by_sex = [0.607, 0.393]

# gender distribution of professors
professors_by_sex = [0.689, 0.310]

primary_schools_per_thousand_people = 6925 / (total_population/1000)
secondary_schools_per_thousand_people = 1688 / (total_population/1000)
pre_universitary_schools_per_thousand_people = 286 / (total_population / 1000)
universities_per_province = 14 / 15

# Distribution of persons by economic activity (both sexes)
# positions in the list represents the following labels:
# 0 agricultura,ganaderia y silvicultura
# 1 Explotacion de minas y canteras
# 2 Industria azucarera
# 3 Industria manufacturera
# 4 Suministro de electricidad, gas y agua
# 5 Construccion
# 6 Comercio y reparacion de efectos personales
# 7 Hoteles y restaurantes
# 8 Transporte, almacenamiento y comunicaciones
# 9 Intermediacion financiera
# 10 Servicios empresariales, actividades inmobiliarias y de alquiler
# 11 Administración pública, defensa, seguridad social
# 12 Ciencia e innovación tecnológica
# 13 Educación
# 14 Salud pública y asistencia social
# 15 Cultura y deporte
# 16 Servicios comunales, sociales y personales
distribution_by_activity_economic = [x/46437 for x in [8025, 263, 223, 462, 3559,
                                                       953, 2644, 4868, 2706, 3262, 321, 737, 2995, 300, 4817, 5133, 1599, 3550]]
# Distribution of women by economic activity
# The positions represent the same as in the previous distribution
women_distribution_by_activity_economic = [
    x/18249 for x in [1385, 51, 47, 96, 1090, 269, 312, 1890, 1326, 637, 219, 361, 1360, 148, 3321, 3640, 698, 1400]]
# Distribution of man by economic activity
# The positions represent the same as in the previous distribution
man_distribution_by_activity_economic = [
    1-x for x in women_distribution_by_activity_economic]
# Population distributions

# positions in the list represents the following ranges:
# < 5, 5-9, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39,40-44, 45-49, 50-54, 55-59,60-64,65>
distribution_by_age_groups = [x/total_population for x in [559705,
                                                           620358,
                                                           578617,
                                                           639797,
                                                           697891,
                                                           722594,
                                                           791652,
                                                           676522,
                                                           660379,
                                                           927867,
                                                           985180,
                                                           934753,
                                                           626848,
                                                           1759432]]

# probability distribution of being a woman or a man
# the first element represents the probability that they are male
distribution_of_man_or_woman = [0.486, 0.496, 1-(0.496+0.486)]

# level of study, the first position represents elementary school or less, the second secondary school,
# the third high school and the last higher education.
enrollment_distribution = [1952, 9995, 24713, 10440]
total_enrollment = 47100

age_groups = [
    [0, 4], [5, 9], [10, 14], [15, 19], [20, 24], [25, 29], [30, 34], [
        35, 39], [40, 44], [45, 49], [50, 54], [55, 59], [60, 64],  [65, 100]
]
# number of members per home variable.
# Position i represents the number of homes with i+1 members
total_houses = 3721042
urban_rural = [2894708, 890488]

# to be checked
neighborhoods_per_thousand_people = 1.0

prob_density = [elem/total_houses for elem in [688205, 956925,
                                               950687, 667271, 281969, 110739, 41575, 16434, 7237]]


class var_generator:
    def __init__(self, prob_density):
        self.prob_density = prob_density

    def generate(self):
        x = random.random()
        current = 0
        for i in range(len(self.prob_density)):
            current += prob_density[i]
            if x < current:
                return i+1
