from functools import partial
from random import betavariate, random


class ParamGenerator:
    def __init__(self,
                 follow_count=None,
                 edge_strength=None,
                 p_follow_back=None,
                 p_rebroadcast=None):
        self._follow_count_func = ParamGenerator._to_generator(follow_count)
        self._edge_strength_func = ParamGenerator._to_generator(edge_strength)
        self._p_follow_back_func = ParamGenerator._to_generator(p_follow_back)
        self._p_rebroadcast_func = ParamGenerator._to_generator(p_rebroadcast)

    @staticmethod
    def _to_generator(arg):
        if arg is None:
            return random
        if isinstance(arg, tuple) and len(arg) == 2:
            return partial(betavariate, alpha=arg[0], beta=arg[1])
        return lambda: arg

    def follow_count(self, n_nodes):
        return int(round(self._follow_count_func() * n_nodes))

    def edge_strength(self):
        return self._edge_strength_func()

    def p_follow_back(self):
        return self._p_follow_back_func()

    def p_rebroadcast(self):
        return self._p_rebroadcast_func()


def beta_params(mean, sd):
    u = mean
    s2 = sd ** 2
    alpha = (-u ** 3 + u ** 2 - u * s2) / s2
    beta = (u ** 3 - 2 * u ** 2 + u * s2 + u - s2) / s2
    if alpha < 0 or beta < 0:
        raise ValueError(f'cannot calculate alpha/beta for mean {mean} and sd {sd}')
    return alpha, beta
