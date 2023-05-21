from pymongo import MongoClient
import random
from odmantic import SyncEngine
from models.population import Population
from models.person import Person

class Node:
    def __init__(self, name,type,household = None, visitors = []):
        self.name = name
        self.type = type  
        self.visitors = visitors
        self.household = household
   
class Graph:
    def __init__(self):
        self.id_nodes = {}
        self.nodes = {}
    def add_node(self, node: Node):
        if node not in self.nodes:
            self.nodes[node] = []
    def add_edge(self, node1:Node, node2:Node):
        if node1 not in self.nodes:
            self.nodes[node1] = []
        self.nodes[node1].append(node2)

def build_graph():
    db = SyncEngine(database='contact_simulation')
    graph = Graph() 
    persons = db.find(Person)
    # myclient = MongoClient("mongodb://localhost:27017/")
    # db = myclient["contact_simulation"]
    # neighborhood_Collection = db["Neighborhood"]
    # school_Collection = db["School"]
    # work_Collection = db["Work"]
    # people_Collection = db["People"]
    create_neighborhood( persons,graph)
    print('crear casas')
    print(len(graph.id_nodes))
    # add_edge_neighborhood(graph)
    # print('edge')
    create_school(persons,graph)
    # print('school')
    create_work(persons,graph)
    # print('work')
    create_random_entertainment_places(graph)
    # print('place en')
    create_random_edges(graph)
    # print('random')
    print(len(graph.id_nodes),'cant nodes final')
    # print('total edges', sum(len(graph.nodes[i]) for i in graph.nodes))
    return graph

def create_neighborhood(data, graph):
    for person in data:
        if not person.household in graph.id_nodes:
            house_node = Node(person.household,"H",person.neighborhood)
            house_node.visitors.append(person.id)
            graph.id_nodes[person.household] = house_node
            graph.add_node(graph.id_nodes[person.household])
        graph.id_nodes[person.household].visitors.append(person.id)
        if not person.neighborhood in graph.id_nodes:
            neighborhood_node = Node(person.neighborhood,'N')
            graph.id_nodes[person.neighborhood] = neighborhood_node
            graph.add_node(graph.id_nodes[person.neighborhood])
        graph.add_edge(graph.id_nodes[person.household],graph.id_nodes[person.neighborhood])
        
def add_edge_neighborhood(graph):
    for node1 in graph.id_nodes:
        for node2 in graph.id_nodes:
            if not node1 == node2 and graph.id_nodes[node1].household == graph.id_nodes[node2].household:
                graph.add_edge(graph.id_nodes[node1],graph.id_nodes[node2])
               
                  

      
def create_school(persons,graph):
    for person in persons:
        if not person.school in graph.nodes:
            graph.id_nodes[person.school] = Node(person.school,"S")
            graph.add_node(graph.id_nodes[person.school])
        graph.add_edge(graph.id_nodes[person.household],graph.id_nodes[person.school])
        
            

def create_work(persons,graph):
    for person in persons:
        if not person.work in graph.nodes:
            graph.id_nodes[person.work] = Node(person.work,"W")
            graph.add_node(graph.id_nodes[person.work])
        graph.add_edge(graph.id_nodes[person.household],graph.id_nodes[person.work])

def create_random_edges(graph):
    for i in range(1000):
        random_node1 = random.choice(list(graph.nodes.keys()))
        random_node2 = random.choice(list(graph.nodes.keys()))
        graph.add_edge(random_node1, random_node2)
        graph.add_edge(random_node2, random_node1) 

def create_random_entertainment_places(graph):
    for i in range(1000):
        new_place = Node(i,"E")
        graph.id_nodes[i] = new_place
        graph.add_node(graph.id_nodes[i])
        random_node = random.choice(list(graph.nodes.keys()))
        graph.add_edge(random_node, new_place)
        graph.add_edge(new_place, random_node)
    

