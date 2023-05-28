
from models.data_source import DataSource, DataSourceFactory
from vectorize_data import vectorize


def generate_random_populations(n: int):
    return [DataSourceFactory().create_random_population() for _ in range(n)]


def vectorize_populations(populations: list[DataSource]):
    # print('mmm', vectorize(populations[0].dict()))
    return [vectorize(population.dict()) for population in populations]


populations = generate_random_populations(100)
vectorized_populations = vectorize_populations(populations)
print(vectorized_populations)
