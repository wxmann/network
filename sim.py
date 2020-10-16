from random import random, choice

DEBUG = False

"""
Independent variables
1-3 <---> strength of connections in the graph
4 <--> compellingness of content transmitted through the graph which decays with time

1. p_ack: likelihood of being receptive to content in network
    (static, property of graph, varies between differet nodes)
2. p_connect_back: strength of connections in network  
    (static, property of graph, varies between different nodes)
3. connect_factor: likelihood of finding "friends" in network. Breadth of network
    (static, property of graph, varies between different nodes)
4. p_rebroadcast: compellingness of content transmitted through network    
    (by message, time-dependent)

Types of Curves
p_ack depends on connect_factor (more friends)
connect_factor looks like beta(alpha=1, beta=3) (exponentially decreasing)
p_connect_back looks like normally distributed RV
p_rebroadcast is  also normally distributed
"""


def create_network(n_nodes, param_generator):
    nodes = []

    for i in range(n_nodes):
        p_ack, p_connect_back, connect_factor = param_generator(n_nodes)
        # trace({'p_ack': p_ack, 'p_connect_back': p_connect_back, 'connect_factor': connect_factor})
        node = Node(i, p_ack, p_connect_back, connect_factor)
        nodes.append(node)

    network = Network(nodes)
    for node in nodes:
        node.obtain_connections(network)

    return network


def trace(thing):
    if DEBUG:
        print(thing)


class Network:
    def __init__(self, nodes):
        self.nodes = nodes
        self.step_index = 0

    def step(self):
        msg = Message(id=self.step_index, p_rebroadcast=0.2)
        choice(self.nodes).broadcast(msg)
        self.step_index += 1
        return msg
        

class Node:
    def __init__(self, index, p_ack, p_connect_back, connect_factor):
        self.index = index
        self.p_ack = p_ack
        self.p_connect_back = p_connect_back
        self.connect_factor = connect_factor
        self.following = set()
        self.followed_by = set()

    def obtain_connections(self, network):
        while len(self.following) < self.connect_factor:
            self.connect(choice(network.nodes))

    def connect(self, other_node):
        if other_node in self.following:
            return
        self.following.add(other_node)
        other_node.followed_by.add(self)
        if random() < other_node.p_connect_back:
            other_node.connect(self)

    def receive(self, msg):
        if random() < self.p_ack and not msg.is_received_by(self):
            msg.track_received_by(self)
            if random() < msg.p_rebroadcast and not msg.is_broadcasted_by(self):
                self.broadcast(msg)

    def broadcast(self, msg):
        msg.track_received_by(self)
        msg.track_broadcast_by(self)
        for node in self.followed_by:
            node.receive(msg)

    def __hash__(self):
        return hash(self.index)

    def __str__(self):
        return f'<Node index {self.index}, p_ack {self.p_ack}>'


class Message:
    def __init__(self, id, p_rebroadcast):
        self.id = id
        self.p_rebroadcast = p_rebroadcast
        self.received_nodes = set()
        self.broadcasted_nodes = set()

    def is_received_by(self, node):
        return node in self.received_nodes

    def is_broadcasted_by(self,  node):
        return node in self.broadcasted_nodes

    def track_received_by(self, node):
        # trace(f'msg {str(self)} received by node {str(node)}')
        self.received_nodes.add(node)

    def track_broadcast_by(self, node):
        # trace(f'msg {str(self)} broadcasted by node {str(node)}')
        self.broadcasted_nodes.add(node)

    def __str__(self):
        return f'<Message, id: {self.id} received by {len(self.received_nodes)} nodes, broadcasted by {len(self.broadcasted_nodes)} nodes>'

