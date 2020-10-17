from random import random, choice, sample

DEBUG = False


def create_network(n_nodes, param_generator):
    nodes = [Node(i) for i in range(n_nodes)]
    network = Network(nodes, param_generator)
    network.init_nodes()
    return network


def trace(thing):
    if DEBUG:
        print(thing)


def test(p):
    assert 0 <= p <= 1
    return random() < p


class Network:
    def __init__(self, nodes, param_generator):
        self.nodes = nodes
        self.param_generator = param_generator
        self.step_index = 0

    def init_nodes(self):
        for node in self.nodes:
            self.onboard(node, self.param_generator.follow_count(len(self.nodes)))

        for node in self.nodes:
            self.evaluate_followers_for(node)

    def onboard(self, node, n):
        for node_to_follow in sample(self.nodes, n):
            node.follow(node_to_follow, self.param_generator.edge_strength())

    def evaluate_followers_for(self, node):
        for follower in node.followers:
            if test(self.param_generator.p_follow_back()):
                node.follow(follower, self.param_generator.edge_strength())

    def step(self, p_rebroadcast=None):
        if p_rebroadcast is None:
            p_rebroadcast = self.param_generator.p_rebroadcast()
        msg = Message(id=self.step_index, p_rebroadcast=p_rebroadcast)
        choice(self.nodes).broadcast(msg)
        self.step_index += 1
        return msg

    def run(self, n, p_rebroadcast=None):
        msgs = [self.step(p_rebroadcast) for _ in range(n)]
        return msgs


class Edge:
    def __init__(self, from_node, to_node, strength):
        self.from_node = from_node
        self.to_node = to_node
        self.strength = strength

    def transmit(self, msg):
        if test(self.strength):
            self.to_node.ack(msg)
            return True
        return False


class Node:
    def __init__(self, index):
        self.index = index
        self.edges = set()
        self.followers = set()

    def ack(self, msg):
        if not msg.is_broadcasted_by(self) and test(msg.p_rebroadcast):
            self.broadcast(msg)
            return True
        return False

    def broadcast(self, msg):
        msg.track_broadcast_by(self)
        for edge in self.edges:
            edge.transmit(msg)

    def follow(self, node, strength):
        node.edges.add(Edge(node, self, strength))
        node.followers.add(self)

    def __hash__(self):
        return hash(self.index)

    def __str__(self):
        return f'<Node index {self.index}>'


class Message:
    def __init__(self, id, p_rebroadcast):
        self.id = id
        self.p_rebroadcast = p_rebroadcast
        self.broadcasted_nodes = set()

    def is_broadcasted_by(self,  node):
        return node in self.broadcasted_nodes

    def track_broadcast_by(self, node):
        self.broadcasted_nodes.add(node)

    def __str__(self):
        return f'<Message, id: {self.id} broadcasted by {len(self.broadcasted_nodes)} nodes>'

