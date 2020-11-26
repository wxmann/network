import random

__all__ = [
    'beta', 'uniform', 'fixed', 'calc_beta_params'
]


def calc_beta_params(mean, sd):
    u = mean
    s2 = sd ** 2
    alpha = (-u ** 3 + u ** 2 - u * s2) / s2
    beta = (u ** 3 - 2 * u ** 2 + u * s2 + u - s2) / s2
    if alpha < 0 or beta < 0:
        raise ValueError(f'cannot calculate alpha/beta for mean {mean} and sd {sd}')
    return alpha, beta


def beta(a, b):
    return _RV(random.betavariate, a=a, b=b)


def uniform(a, b):
    return _RV(random.uniform, a=a, b=b)


def fixed(val):
    return _RV(lambda: val)


class _RV:
    def __init__(self, func, **params):
        self._func = func
        self._params = params
        self._factor = 1

    @property
    def params(self):
        return dict(self._params)

    def __call__(self):
        return self._factor * self._func(*self._params.values())

    def __mul__(self, other):
        self._factor = other

    def __rmul__(self, other):
        self._factor = other
