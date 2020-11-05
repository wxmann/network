from functools import partial
from random import betavariate, random
import math
from collections import namedtuple

applyable = namedtuple('applyable', ['func', 'deterministic'])


class ParamGenerator:
    def __init__(self,
                 follow_count=None,
                 edge_strength=None,
                 p_follow_back=None,
                 p_rebroadcast=None):
        self._follow_count = ParamGenerator._to_generator(follow_count)
        self._edge_strength = ParamGenerator._to_generator(edge_strength)
        self._p_follow_back = ParamGenerator._to_generator(p_follow_back)
        self._p_rebroadcast = ParamGenerator._to_generator(p_rebroadcast)

    @staticmethod
    def _to_generator(arg):
        if arg is None:
            return applyable(func=random, deterministic=False)
        if isinstance(arg, tuple) and len(arg) == 2:
            func = partial(betavariate, alpha=arg[0], beta=arg[1])
            return applyable(func=func, deterministic=False)

        return applyable(func=lambda: arg, deterministic=True)

    def follow_count(self, n_nodes):
        if self._follow_count.deterministic:
            return self._follow_count.func()
        return int(math.ceil(self._follow_count.func() * n_nodes))

    def edge_strength(self):
        return self._edge_strength.func()

    def p_follow_back(self):
        return self._p_follow_back.func()

    def p_rebroadcast(self):
        return self._p_rebroadcast.func()


def beta_params(mean, sd):
    u = mean
    s2 = sd ** 2
    alpha = (-u ** 3 + u ** 2 - u * s2) / s2
    beta = (u ** 3 - 2 * u ** 2 + u * s2 + u - s2) / s2
    if alpha < 0 or beta < 0:
        raise ValueError(f'cannot calculate alpha/beta for mean {mean} and sd {sd}')
    return alpha, beta
