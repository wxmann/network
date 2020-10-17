from functools import partial
from random import betavariate


class ParamGenerator:
    def __init__(self):
        self.n_nodes = None
        self.connect_factor = None
        self.p_ack = None
        self.p_connect_back = None

    def __call__(self, n_nodes):
        self.n_nodes = n_nodes
        self.generate_connect_factor()
        self.generate_p_ack()
        self.generate_p_connect_back()
        return self.p_ack, self.p_connect_back, self.connect_factor

    def generate_connect_factor(self):
        raise NotImplementedError

    def generate_p_ack(self):
        raise NotImplementedError

    def generate_p_connect_back(self):
        raise NotImplementedError


class DefaultParamGenerator(ParamGenerator):
    def __init__(self,
                 connect_beta_params=None,
                 base_p_ack=0.25,
                 p_connect_back_fixed=0.5):
        super().__init__()
        if connect_beta_params is None:
            connect_beta_params = dict(alpha=1, beta=100)

        self.connect_beta = partial(betavariate, **connect_beta_params)
        self.p_connect_back_fixed = p_connect_back_fixed
        self.base_p_ack = base_p_ack

    def generate_connect_factor(self):
        self.connect_factor = int(round(self.n_nodes * self.connect_beta()))

    def generate_p_ack(self):
        self.p_ack = self.base_p_ack + (1 - self.base_p_ack) * self.connect_factor / self.n_nodes

    def generate_p_connect_back(self):
        self.p_connect_back = self.p_connect_back_fixed


defaults = DefaultParamGenerator()
