from pymongo import MongoClient
import random
import numpy as np
from odmantic import SyncEngine
from models.contact_matrix import ContactMatrix
from models.population import Population
from models.person import Person
from .places_graph import Graph, build_graph, Node
import pickle
from pathlib import Path
from World import World
from sklearn.preprocessing import StandardScaler
import pandas as pd
from vectorize_data import vectorize
from models.data_source import DataSource


def run_step_of_simulation(population, graph: Graph, db: SyncEngine, matrix, w: World, save_matrices=True):

    for person in population:
        try:
            update_visitors(person, graph.id_nodes[person.current_place])
            move = build_move_distribution(
                person.last_place, person.current_place, graph, person.study, person.work)
            move.visitors.append(person)
        except KeyError():
            print("unknown place, skipping")
            continue
    full_matrix = get_contact_matrix(graph, population, matrix, w)

    return full_matrix


def build_move_distribution(last_position: str, actual_position: str, graph: Graph, isSchool, isWork) -> Node:
    node_actual = graph.id_nodes[actual_position]

    possible_next_moves = graph.nodes[node_actual]
    move_list = []
    prob_list = [0.0]*len(possible_next_moves)
    for i in range(len(possible_next_moves)):
        move_list.append(possible_next_moves[i])
        if possible_next_moves[i].type == 'H':
            if not isSchool and not isWork:
                prob_list[i] = 0.4
            elif not graph.id_nodes[last_position].type == 'H':
                if graph.id_nodes[last_position].type == 'W' or graph.id_nodes[last_position].type == 'S':
                    prob_list[i] = 0.3

                else:
                    prob_list[i] = 0.2
            else:
                prob_list[i] = 0.2

        elif possible_next_moves[i].type == 'W':
            if not isWork:
                prob_list[i] = 0.1

            elif isWork and not graph.id_nodes[last_position].type == 'W':
                if graph.id_nodes[last_position].type == 'H':
                    prob_list[i] = 0.2
                else:
                    prob_list[i] = 0.2
            else:
                prob_list[i] = 0.1
        elif possible_next_moves[i] == 'S':
            if not isSchool:
                prob_list[i] = 0.1
            elif isSchool and not graph.id_nodes[last_position].type == 'S':
                if graph.id_nodes[last_position].type == 'H':
                    prob_list[i] = 0.2
                else:
                    prob_list[i] = 0.2
            else:
                prob_list[i] = 0.2

        elif possible_next_moves[i] == 'N':
            prob_list[i] = 0.1
        else:
            prob_list[i] = 0.1

    prob_list = np.array(prob_list) / np.linalg.norm(prob_list, ord=1)
    position = np.random.choice(a=len(move_list), p=prob_list, size=1)[0]
    if not move_list[position].type == 'N':
        return move_list[position]
    else:
        if len(graph.nodes[move_list[position]]) == 0:
            return graph.id_nodes[actual_position]
        else:
            house_random = random.randint(
                0, len(graph.nodes[move_list[position]])-1)
            return graph.nodes[move_list[position]][house_random]


def update_visitors(person: Person, current_place: Node):
    len_visitor = len(current_place.visitors)-1
    i = 0
    while (i < len_visitor):
        i += 1
        if current_place.visitors[i] == person:
            current_place.visitors.pop(i)
            len_visitor -= 1


def get_contact_matrix(graph: Graph, population, matrix, w: World):
    z = 0
    for node in graph.nodes.keys():
        if node.visitors == []:
            continue
        if not node.type == "H":

            number_contact = len(node.visitors)/10
            get_normal_distribution = np.arange(0, len(node.visitors))
            contacts = np.random.choice(
                a=len(node.visitors), size=int(number_contact))
            for i in range(len(contacts)):
                for j in range(i+1, len(contacts)):
                    # if node.type == 'S':
                    #     Schoolmatrix[w.get_age_group(node.visitors[contacts[i]].age),w.get_age_group(node.visitors[contacts[j]].age)] += 1
                    #     Schoolmatrix[w.get_age_group(node.visitors[contacts[j]].age),w.get_age_group(node.visitors[contacts[i]].age)] += 1
                    # elif node.type == 'W':
                    #     Workmatrix[w.get_age_group(node.visitors[contacts[i]].age),w.get_age_group(node.visitors[contacts[j]].age)] += 1
                    #     Workmatrix[w.get_age_group(node.visitors[contacts[j]].age),w.get_age_group(node.visitors[contacts[i]].age)] += 1
                    matrix[w.get_age_group(node.visitors[i].age), w.get_age_group(
                        node.visitors[j].age)] += 1
                    matrix[w.get_age_group(node.visitors[j].age), w.get_age_group(
                        node.visitors[i].age)] += 1
        else:
            for i in range(len(node.visitors)):
                for j in range(i+1, len(node.visitors)):
                    # Housematrix[w.get_age_group(node.visitors[i].age),w.get_age_group(node.visitors[j].age)] += 1
                    # Housematrix[w.get_age_group(node.visitors[j].age),w.get_age_group(node.visitors[i].age)] += 1
                    matrix[w.get_age_group(node.visitors[i].age), w.get_age_group(
                        node.visitors[j].age)] += 1
                    matrix[w.get_age_group(node.visitors[j].age), w.get_age_group(
                        node.visitors[i].age)] += 1
        z += 1
    # print('sali del for')
    # print(matrix)
    return matrix


def save_graph_to_file(graph: Graph):
    with open('graph.obj', 'wb') as file:
        pickle.dump(graph, file)


def load_graph_from_file() -> Graph:
    with open('graph.obj', 'rb') as file:
        return pickle.load(file)


def normalize_matrice(graph: Graph, matrix):
    total_people_by_age_group = [graph.age_dict[i] for i in graph.age_dict]
    for i in range(len(matrix)):
        to_sum = total_people_by_age_group[i]
        summed_values = np.array([to_sum * total_people_by_age_group[j]
                                 for j in range(len(total_people_by_age_group))])
        matrix[i] = matrix[i] / summed_values

    return matrix


def run_simulation(world: World, use_cache=True, save_matrices=True):
    db = SyncEngine(database='contact_simulation_2n')

    use_cache = False
    if use_cache and Path('graph.obj').is_file():
        graph = load_graph_from_file()
        print('Graph loaded with pickle')
    else:
        print('Starting graph creation')
        graph = build_graph(world)
        save_graph_to_file(graph)
        print('done graph')
    full_matrix = np.zeros((14, 14))
    # school_matrix =np.zeros((14,14))
    # work_matrix= np.zeros((14,14))
    # house_matrix=np.zeros((14,14))
    n_days = 10
    population = db.find(Person)
    for i in range(n_days):
        full_matrix = run_step_of_simulation(
            population, graph, db, full_matrix, world)

        print(i) 
    db.remove(Person)
    print("Done simulating, building matrix")
    save_full_matrix = normalize_matrice(graph, full_matrix)/n_days
    vector_data = vectorize(world.data_source.dict())
    save_full_in_db = ContactMatrix(category='full_matrix', vector=vector_data.tolist(
    ), data=save_full_matrix.tolist(), simulation_type='graph')
    db.save(save_full_in_db)

    print('termine')
