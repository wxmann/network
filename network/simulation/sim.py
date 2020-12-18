import contextlib
import random
from itertools import islice

from pathos.multiprocessing import ProcessingPool

from network.randoms import fix_random


class Simulation:
    def __init__(self, transmission, runner=None):
        self._transmission = transmission
        if not runner:
            self._runner = self._transmission
        else:
            self._runner = runner(transmission)

        self._saved_path = []
        self._path_completed = False
        self._tracked_index = 0

    def _exec_transmission(self, steps):
        while steps is None or self._tracked_index < steps:
            try:
                next_path_segment = next(self._runner)
                self._saved_path.append(next_path_segment)
                self._tracked_index += 1
            except StopIteration:
                self._path_completed = True
                break

    def path(self, index=None):
        if index is None or (not self._path_completed and index >= len(self._saved_path)):
            self._exec_transmission(index)
        max_index = len(self._saved_path) if index is None else index
        return islice(self._saved_path, max_index)

    @property
    def originating_node(self):
        return self._transmission.originating_node

    @property
    def transmission(self):
        return self._transmission

    @property
    def history(self):
        return self._transmission.history


def test(p):
    if callable(p):
        return random.random() < p()
    elif 0 <= p <= 1:
        return random.random() < p
    else:
        raise ValueError('p must be between 0 and 1')


def run_simulations(*sims, to=None, workers=None, reproducible=True):
    def run_single_sim(sim):
        ctx = fix_random if reproducible else contextlib.nullcontext
        with ctx():
            sim.path(to)
            return sim

    if len(sims) == 1:
        return run_single_sim(sims[0])

    if workers is None:
        workers = min(len(sims), 4)
    pool = ProcessingPool(workers)
    return pool.map(run_single_sim, sims)


def create_runner(before=None, after=None):
    return lambda transmission: _BeforeAndAfterRunner(transmission, before, after)


class _BeforeAndAfterRunner:
    def __init__(self, transmission, before, after):
        self.before = before
        self.after = after
        self.transmission = transmission

    def __iter__(self):
        return self

    def __next__(self):
        if self.before:
            self.before(self.transmission)
        next(self.transmission)
        if self.after:
            self.after(self.transmission)
