import datetime
import pandas as pd

from World import World
from data_loader import DataLoader


from models.person import Person
import asyncio
from simulation.places_graph import build_graph
from simulation.simulationv2 import run_simulation

def main():

    dl = DataLoader()
    # print('initializing database')
    # client = AsyncIOMotorClient("mongodb://localhost:27017/")

    # Initialize beanie with the Product document class and a database
    # await init_beanie(database=client.db_name, document_models=[Person, Household, School, Workplace])
    w = World('data.json')

    print("Generating Population")
    # w.generate_population("pinar", n_processes=40)

    print("Done!, Simmulating days now...")
    # build_graph()
    
    # print('done graph')
    run_simulation(w)
    # w.run_simulation("pinar", 100)
    # print("Building Matrix")
    # labels = [str(i[0])+"-"+str(i[1]) for i in dl.age_groups]

    # m = w.generate_contact_matrix("CUBA")
    # df = pd.DataFrame(m, columns=labels)

    # df.to_csv("matrix.csv")


if __name__ == '__main__':
    main()


# build_graph()