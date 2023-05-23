from pymongo import MongoClient
import random
import numpy as np
from odmantic import SyncEngine
from models.population import Population
from models.person import Person
from .places_graph import Graph,build_graph,Node
import pickle
from pathlib import Path
from World import World

def run_step_of_simulation(graph : Graph,db: SyncEngine ,matrix , w : World):
        
    
    # myclient = MongoClient("mongodb://localhost:27017/")
    # db = myclient["contact_simulation"]
    # population_Collection = db["Person"
    population = db.find(Person)
    for person in population:
        move = build_move_distribution(person.last_place,person.current_place,graph)
        # print(type(move), ' es un node')
        # print(move in graph.nodes)
        # print(type(person))
        # print(type(move), 'que tu ere')

        move.visitors.append(person)
        # print(type(move.visitors[-1]), 'que tu ere')
    print('termine esto')
    return get_contact_matrix(graph,population,matrix,w)


def build_move_distribution(last_position:str,actual_position:str,graph:Graph) -> Node:
    node_actual = graph.id_nodes[actual_position]
    possible_next_moves = graph.nodes[node_actual]
    move_list = [] 
    prob_list =[0.0]*len(possible_next_moves)
    # print(prob_list,'moves')
    # pro_move_random = (len(possible_next_moves) - 2)/0.3
    for i in range (len(possible_next_moves)):
        move_list.append(possible_next_moves[i])
        if possible_next_moves[i].type == 'H':
            if not graph.id_nodes[last_position].type == 'H':
                if last_position == 'W':
                    prob_list[i] = 0.5
                else :
                    prob_list[i] = 0.4
            else:
                prob_list[i] = 0.3
        elif possible_next_moves[i].type == 'W':
            if not graph.id_nodes[last_position].type== 'W':
                if last_position == 'H':
                    prob_list[i] = 0.5
                else :
                    prob_list[i] = 0.4
            else:
                prob_list[i] = 0.4
        elif possible_next_moves[i] == 'N' or possible_next_moves[i] == 'S':
            prob_list[i] = 0.1
        else:
            prob_list[i] = 0.1
    # print(prob_list, 'kdkd')
    prob_list = np.array(prob_list) / np.linalg.norm(prob_list, ord=1)
    # print(move_list)
    # print(prob_list)
    position = np.random.choice(a =len(move_list), p = prob_list,size=1)[0]
    # print(position, ' a ver')
    # print(position)
    # print(move_list, 'mira')
    # print(move_list[position], ' que bola')
    if not move_list[position].type == 'N':
        return move_list[position]
    else:
        # print(graph.nodes[move_list[position]], ' a ver si es normal')
        if len(graph.nodes[move_list[position]] )== 0:
            return graph.id_nodes[actual_position]
        else:
            house_random = random.randint(0,len(graph.nodes[move_list[position]])-1)
            # print(house_random, ' esto es un numero ??')
            return graph.nodes[move_list[position]][house_random]

                
def get_contact_matrix(graph: Graph,population,matrix,w : World):
    print(len(graph.nodes.keys()))
    for node in graph.nodes.keys():
        if node.visitors == []:
            continue
        if not node.type == "H":
            number_contact = len(node.visitors)/3
            get_normal_distribution = np.arange(0,node.visitors)
            prob = np.array(get_normal_distribution) / np.linalg.norm(get_normal_distribution, ord=1)
            contacts = np.random.choice(a = len(node.visitors),p = prob, size = int(number_contact))
            for i in range(len(contacts)):
               for j in range(i+1,len(contacts)): 
                    matrix[w.get_age_group(node.visitors[contacts[i]].age),w.get_age_group(node.visitors[contacts[j]].age)] += 1
                    matrix[w.get_age_group(node.visitors[contacts[j]].age),w.get_age_group(node.visitors[contacts[i]].age)] += 1
                      
        else:
            for i in range(len(node.visitors)):
                for j in range(i+1,len(node.visitors)):
                    # print(type(node.visitors[0]), ' a ver ')
                    # print(type(node.visitors[-1]), 'mmm')
                    # print(node.visitors[i],'uno')

                    matrix[w.get_age_group(node.visitors[i].age),w.get_age_group(node.visitors[j].age)] += 1
                    matrix[w.get_age_group(node.visitors[j].age),w.get_age_group(node.visitors[i].age)] += 1
        print(matrix)
                
    return matrix
    

def save_graph_to_file(graph: Graph):
    with open('graph.obj', 'wb') as file:
        pickle.dump(graph, file)


def load_graph_from_file() -> Graph:
    with open('graph.obj', 'rb') as file:
        return pickle.load(file)


def run_simulation(world : World,use_cache=True):
    db = SyncEngine(database='contact_simulation')
    # use_cache = False
    if use_cache and Path('graph.obj').is_file():
        graph = load_graph_from_file()
        print('Graph loaded with pickle')
    else:
        print('Starting graph creation')
        graph = build_graph()
        save_graph_to_file(graph)
        print('done graph')
    # print(len(graph.nodes))
    # print(len(graph.id_nodes))
    
        
    M = matrix = np.zeros((14,14))
    # for i in range(3):

    M = run_step_of_simulation(graph,db,M ,world)
    print(M)


        
    


