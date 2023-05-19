from pymongo import MongoClient
import random
import places_graph

def run_step_of_simulation():
    graph =places_graph.build_graph()
    myclient = MongoClient("mongodb://localhost:27017/")
    db = myclient["contact_simulation"]
    population_Collection = db["Person"]
    for document in population_Collection.find():
        move = build_move_distribution(document["last_position"],document["actual_position"],document["age"],document["work"],document["school"])
        execute_move(move,graph)
    return get_contact_matrix(graph)



def build_move_distribution(last_position,actual_position,age,work,school):
    pass

def execute_move(move,graph):
    pass

def get_contact_matrix(graph):
    pass


