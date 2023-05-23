from pymongo import MongoClient
import random
from odmantic import SyncEngine
from models.population import Population
from models.person import Person
from uuid import UUID, uuid4
from typing import Self

class Node:
    def __init__(self, name,type,household = None, visitors :list[Person] = []):
        self.name = name
        self.type = type  
        self.visitors = visitors
        self.household = household
   
class Graph:
    def __init__(self):
        self.id_nodes : dict[str,Node] = {}
        self.nodes:dict[Node,list[Node]] = {}
    def add_node(self, node: Node):
        if node not in self.nodes:
            self.nodes[node] = []
    def add_edge(self, node1:Node, node2:Node):
        if node1 not in self.nodes:
            self.nodes[node1] = []
        if node2 not in self.nodes:
            self.nodes[node2] = []
        self.nodes[node1].append(node2)
        self.nodes[node2].append(node1)

def build_graph():
    db = SyncEngine(database='contact_simulation')
    graph = Graph() 
    persons = list(db.find(Person))
    create_neighborhood( persons,graph)
    create_school(persons,graph)
    create_work(persons,graph)
    create_random_entertainment_places(graph)
    create_random_edges(graph)
    return graph

def create_neighborhood(data , graph: Graph):
    for person in data:
        # print(type(person), 'xq repiiiin')
        if not person.household in graph.id_nodes:
            house_node = Node(person.household,"H",person.neighborhood)
            house_node.visitors.append(person)
            # print(type(house_node.visitors[-1]),'a ver aki')
            graph.id_nodes[person.household] = house_node
            graph.add_node(graph.id_nodes[person.household])
        graph.id_nodes[person.household].visitors.append(person)
        # print( type(graph.id_nodes[person.household].visitors[-1]),'esta pin que ')
        if not person.neighborhood in graph.id_nodes:
            neighborhood_node = Node(person.neighborhood,'N')
            graph.id_nodes[person.neighborhood] = neighborhood_node
            graph.add_node(graph.id_nodes[person.neighborhood])
        graph.add_edge(graph.id_nodes[person.household],graph.id_nodes[person.neighborhood])
        # graph.add_edge(graph.id_nodes[person.neighborhood],graph.id_nodes[person.household])
        
def add_edge_neighborhood(graph:Graph):
    for node1 in graph.id_nodes:
        for node2 in graph.id_nodes:
            if not node1 == node2 and graph.id_nodes[node1].household == graph.id_nodes[node2].household:
                graph.add_edge(graph.id_nodes[node1],graph.id_nodes[node2])
               
                  
def create_school(persons,graph:Graph):
    for person in persons:
        if person.school == None :
            continue
        if not person.school in graph.id_nodes:
            graph.id_nodes[person.school] = Node(person.school,"S")
            graph.add_node(graph.id_nodes[person.school])
        # print(person.school, person.household, ' seraaaaa')
        graph.add_edge(graph.id_nodes[person.household],graph.id_nodes[person.school])
        
            

def create_work(persons,graph:Graph):
    for person in persons:
        if not person.work in graph.id_nodes:
            graph.id_nodes[person.work] = Node(person.work,"W")
            graph.add_node(graph.id_nodes[person.work])
        graph.add_edge(graph.id_nodes[person.household],graph.id_nodes[person.work])

def create_random_edges(graph:Graph):
    for i in range(1000):
        random_node1 = random.choice(list(graph.nodes.keys()))
        random_node2 = random.choice(list(graph.nodes.keys()))
        graph.add_edge(random_node1, random_node2)
        graph.add_edge(random_node2, random_node1) 

def create_random_entertainment_places(graph:Graph):
    for i in range(1000):
        id = str(uuid4())
        new_place = Node(id,"E")
        graph.id_nodes[id] = new_place
        graph.add_node(new_place)
        random_node = random.choice(list(graph.nodes.keys()))
        graph.add_edge(random_node, new_place)
        graph.add_edge(new_place, random_node)
  
    
    

