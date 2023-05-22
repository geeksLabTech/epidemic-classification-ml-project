from pymongo import MongoClient
import random
import numpy as np
from odmantic import SyncEngine
from models.population import Population
from models.person import Person
from .places_graph import Graph,build_graph

def run_step_of_simulation(graph : Graph,db,matrix):
        
    node_list = list(graph.nodes.keys())
    # myclient = MongoClient("mongodb://localhost:27017/")
    # db = myclient["contact_simulation"]
    # population_Collection = db["Person"
    population = db.find(Person)
    for person in population:
        move = build_move_distribution(person.last_place,person.current_place,person.age,person.work,person.school,graph)
        node_list[move].visitors.append(person.id)
    return get_contact_matrix(graph,population,matrix)


def build_move_distribution(last_position,actual_position,age,work,school,graph):
    node_actual = graph.id_nodes[actual_position]
    possible_next_moves = graph.nodes[node_actual]
    move_list = [] 
    prob_list =[0.0]*len(possible_next_moves)
    print(prob_list,'moves')
    pro_move_random = (len(possible_next_moves) - 2)/0.3
    for i in range (len(possible_next_moves)):
        move_list.append(i)
        if possible_next_moves[i].type == 'H':
            if not last_position.type == 'H':
                if last_position == 'W':
                    prob_list[i] = 0.4
                else :
                    prob_list[i] = 0.3
            else:
                prob_list[i] = 0.2
        elif possible_next_moves[i] == 'W':
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
    if not move_list[position].type == 'N':
        return move_list[position]
    else:
        house_random = random.randint(0,len(graph.nodes[move_list[position]]))
        return graph.nodes[move_list[position]][house_random]

                
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
    

def run_simulation():
    db = SyncEngine(database='contact_simulation')
    graph =build_graph()
    print('done graph')
    M = matrix = np.zeros((14,14))
    for i in range(3):

        M = run_step_of_simulation(graph,db,M )
    print(M)


        
    


