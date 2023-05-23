import datetime
import pandas as pd

from models.person import Person
import pandas as pd

from World import World


def main():
    # print('initializing database')
    # client = AsyncIOMotorClient("mongodb://localhost:27017/")

    # Initialize beanie with the Product document class and a database
    # await init_beanie(database=client.db_name, document_models=[Person, Household, School, Workplace])
    w = World('data.json')

    n_days = 2
    # # print("Generating Population")
    w.generate_population("pinar", n_processes=40)

    # print(w.db.count(Person))
    print("Done!, Simmulating days now...")

    w.run_simulation("pinar", n_days)

    print("Building Matrix")
    w.generate_contact_matrix("pinar", n_days)

    labels = [str(i[0])+"-"+str(i[1]) for i in w.data_source.age_groups]

    final_mat = w.mat/(2*n_days)
    final_mat = final_mat / w.mat_ages
    # final_mat = (final_mat.transpose()) / w.mat_ages

    df = pd.DataFrame(final_mat, columns=labels)
    df.to_csv("matrix.csv")


if __name__ == '__main__':
    main()
