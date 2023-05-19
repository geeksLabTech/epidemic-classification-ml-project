from pymongo import MongoClient
import random
class Node:
    def __init__(self, name,type, visitors = []):
        self.name = name
        self.type = type  
        self.visitors = visitors 
   
class Graph:
    def __init__(self):
        self.nodes = {}
    def add_node(self, node: Node):
        if node not in self.nodes:
            self.nodes[node] = []
    def add_edge(self, node1:Node, node2:Node):
        if node1 not in self.nodes:
            self.nodes[node1] = []
        self.nodes[node1].append(node2)

def build_graph():
    graph = Graph() 
    myclient = MongoClient("mongodb://localhost:27017/")
    db = myclient["contact_simulation"]
    neighborhood_Collection = db["Neighborhood"]
    school_Collection = db["School"]
    work_Collection = db["Work"]
    # people_Collection = db["People"]
    create_neighborhood( neighborhood_Collection,graph)
    create_school(school_Collection,neighborhood_Collection,graph)
    create_work(work_Collection,neighborhood_Collection,graph)
    create_random_nodes(graph)
    return graph

def create_neighborhood(data, graph):
    for document in data.find():
    # print(document)
        for neighborhoods in document["neighborhood"]:
            for i in range(len(neighborhoods)) - 1:
                graph.add_edge(Node(neighborhoods[i]["neighborhoods"], "H"), Node(neighborhoods[i + 1]["neighborhoods"],"H"))
                graph.add_edge(Node(neighborhoods[i + 1]["neighborhoods"],"H"), Node(neighborhoods[i]["neighborhoods"],"H"))
            for i in range(5):
                random_node1 = random.choice(list(graph.nodes.keys()))
                random_node2 = random.choice(list(graph.nodes.keys()))
                graph.add_edge(random_node1, random_node2)
                graph.add_edge(random_node2, random_node1)
        
def create_school(school_Collection,neighborhood_Collection,graph):
    for school in school_Collection.find():
        graph.add_node(Node(school["id"],"S"))
        for students in school["students"]:
            for document in neighborhood_Collection.find():
                for neighborhoods in document["neighbordood"]:
                    for person in neighborhoods:
                        if person["id"] == students:
                            graph.add_edge(Node(school["id"],"S"), Node(person["id"],"H"))
                            graph.add_edge(Node(person["id"],"H"), Node(school["id"],"S"))

def create_work(work_Collection,neighborhood_Collection,graph):
    for work in work_Collection.find():
        graph.add_node(Node(work["id"],"W"))
        for workers in work["workers"]:
            for document in neighborhood_Collection.find():
                for neighborhoods in document["neighbordood"]:
                    for person in neighborhoods:
                        if person["id"] == workers:
                            graph.add_edge(Node(work["id"],"W"), Node(person["id"],"H"))
                            graph.add_edge(Node(person["id"],"H"), Node(work["id"],"W"))

def create_random_nodes(graph):
    for i in range(1000):
        random_node1 = random.choice(list(graph.nodes.keys()))
        random_node2 = random.choice(list(graph.nodes.keys()))
        graph.add_edge(random_node1, random_node2)
        graph.add_edge(random_node2, random_node1) 