from pymongo import MongoClient
import random
import numpy as np
import places_graph

def run_step_of_simulation(matrix = None):
    if not matrix:
        matrix = np.zeros((14,14))
    graph =places_graph.build_graph()
    node_list = list(graph.nodes.keys())
    myclient = MongoClient("mongodb://localhost:27017/")
    db = myclient["contact_simulation"]
    population_Collection = db["Person"]
    for document in population_Collection.find():
        move = build_move_distribution(document["last_position"],document["actual_position"],document["age"],document["work"],document["school"])
        node_list[move].visitors.append(document["id"])
    return get_contact_matrix(graph,population_Collection,matrix)




def build_move_distribution(last_position,actual_position,age,work,school):
    pass



def get_contact_matrix(graph,population,matrix):
    for node in graph.nodes:
        if not node.type == "H":
            number_contact = len(node.visitors)/3
            contact = random.sample(node.visitors,int(number_contact))
            row = population.find({"id ":str(node.name)})
            column = population.find({"id ":node.visitors[contact].name})
            matrix[row,column] += 1
        else:
            for i in range(1,len(node.visitors)):
                row = population.find({"id ":str(node.name)})
                column = population.find({"id ":node.visitors[i].name})
                matrix[row,column] += 1 
    return matrix
    

                 

        
    


