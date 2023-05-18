from pymongo import MongoClient
import random
class Node:
    def __init__(self, name):
        self.name = name      
   
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
    people_Collection = db["People"]
    create_neighborhood( neighborhood_Collection,graph)
    create_school(school_Collection,neighborhood_Collection,people_Collection,graph)
     


def create_neighborhood(data, graph):
    for document in data.find():
    # print(document)
        for neighborhoods in document["neighborhood"]:
            for i in range(len(neighborhoods)) - 1:
                graph.add_edge(Node(neighborhoods[i]["neighborhoods"]), Node(neighborhoods[i + 1]["neighborhoods"]))
                graph.add_edge(Node(neighborhoods[i + 1]["neighborhoods"]), Node(neighborhoods[i]["neighborhoods"]))
            for i in range(5):
                random_node1 = random.choice(list(graph.nodes.keys()))
                random_node2 = random.choice(list(graph.nodes.keys()))
                graph.add_edge(random_node1, random_node2)
                graph.add_edge(random_node2, random_node1)
        

            