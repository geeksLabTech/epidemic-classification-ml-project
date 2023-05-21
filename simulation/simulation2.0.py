from pymongo import MongoClient
import random
import numpy as np
import places_graph
from odmantic import SyncEngine
from models.population import Population
from models.person import Person


def run_step_of_simulation(matrix = None):
    db = SyncEngine(database='contact_simulation')
    if not matrix:
        matrix = np.zeros((14,14))
    graph =places_graph.build_graph()
    node_list = list(graph.nodes.keys())
    # myclient = MongoClient("mongodb://localhost:27017/")
    # db = myclient["contact_simulation"]
    # population_Collection = db["Person"
    population = db.find(Person)
    for person in population:
        move = build_move_distribution(person.last_position,person.actual_position,person.age,person.work,person.school,graph)
        node_list[move].visitors.append(person.id)
    return get_contact_matrix(graph,population,matrix)




def build_move_distribution(last_position,actual_position,age,work,school,graph):
    node_actual = graph.id_node[actual_position]
    possible_next_moves = graph.nodes[node_actual]
    move_list = [] 
    prob_list =[]*len(possible_next_moves)
    pro_move_random = (len(possible_next_moves) - 2)/0.3
    for i in possible_next_moves:
        move_list.append(i)
        if i.type == 'H':
            if not last_position.type == 'H':
                if last_position == 'W':
                    prob_list[i] = 0.4
                else :
                    prob_list[i] = 0.3
            else:
                prob_list[i] = 0.2
        elif i.type == 'W':
            if not last_position.type == 'W':
                if last_position == 'H':
                    prob_list[i] = 0.4
                else :
                    prob_list[i] = 0.3
            else:
                prob_list[i] = 0.2
        else:
            prob_list[i] = pro_move_random
    position = np.random.choice(prob_list)
    return move_list[position]

                
def get_contact_matrix(graph,population,matrix):
    for node in graph.nodes:
        if not node.type == "H":
            number_contact = len(node.visitors)/3
            contact = random.sample(node.visitors,int(number_contact)) #TODO Poison distribution
            row = population.find({"id ":str(node.name)})
            column = population.find({"id ":node.visitors[contact].name})
            matrix[row,column] += 1
        else:
            for i in range(1,len(node.visitors)):
                row = population.find({"id ":str(node.name)})
                column = population.find({"id ":node.visitors[i].name})
                matrix[row,column] += 1 
    return matrix
    

                 

        
    


