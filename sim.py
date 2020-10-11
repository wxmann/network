from random import random, sample, choice

DEBUG = True

def create_network(n_nodes):
    # for now, hard code this
    p_ack = 0.35
    p_connect_back = 0.6
    connect_factor = 20
    nodes = []

    for i in range(n_nodes):
        node = Node(i, p_ack, p_connect_back)
        nodes.append(node)

    for node in nodes:
        nodes_to_follow = sample(nodes, connect_factor)
        for node_to_follow in nodes_to_follow:
            node.connect(node_to_follow)

    return Network(nodes)


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
        

class Node:
    def __init__(self, index, p_ack, p_connect_back):
        self.index = index
        self.p_ack = p_ack
        self.p_connect_back = p_connect_back
        self.following = set()
        self.followed_by = set()

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
        return hash((self.index))

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
        trace(f'msg {str(self)} received by node {str(node)}')
        self.received_nodes.add(node)

    def track_broadcast_by(self, node):
        trace(f'msg {str(self)} broadcasted by node {str(node)}')
        self.broadcasted_nodes.add(node)

    def __str__(self):
        return f'<Message, id: {self.id} received by {len(self.received_nodes)} nodes, broadcasted by {len(self.broadcasted_nodes)} nodes>'


if __name__ == '__main__':
    network = create_network(2000)
    network.step()
