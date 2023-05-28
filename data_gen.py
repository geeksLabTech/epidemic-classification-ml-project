from models.data_source import DataSourceFactory
from data_loader import DataLoader
import pandas as pd
import numpy as np
import json
from World import World


def generate_dataset(n_datasets: int = 1000):
    for it in range(n_datasets):
        print(f"{it}/{n_datasets}")
        n_days = 15

        file = f"dataset/data_{it}.json"

        data = DataSourceFactory().create_random_population().__dict__

        with open(file, "w") as f:
            json.dump(data, f)

        dl = DataLoader(file)

        w = World(dl)

        w.generate_population(file)
        w.run_simulation(file, n_days=n_days)
        w.generate_contact_matrix(file, n_days)

        labels = [str(i[0])+"-"+str(i[1]) for i in w.data_source.age_groups]

        for i in w.mat:
            final_mat = w.mat[i]/(2*n_days)
            final_mat = final_mat / w.mat_ages
            # final_mat = (final_mat.transpose()) / w.mat_ages

            df = pd.DataFrame(final_mat, columns=labels)
            df.to_csv(f"dataset/data_{it}/matrix_{i}.csv")

generate_dataset()