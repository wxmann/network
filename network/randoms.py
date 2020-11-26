import pickle
import random
from contextlib import contextmanager
from pathlib import Path


def get_fixed_state():
    pkl_dir = Path(__file__).resolve().parent
    with open(f'{pkl_dir}/resources/sim_state.pkl', 'rb') as f:
        return pickle.load(f)


def fixed_random():
    rand = random.Random()
    rand.setstate(get_fixed_state())
    return rand


@contextmanager
def fix_random(rand=None, state=None):
    random_ = rand or random
    saved_state = random_.getstate()
    try:
        fixed_state = state or get_fixed_state()
        random_.setstate(fixed_state)
        yield
    finally:
        random_.setstate(saved_state)