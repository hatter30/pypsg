

import pytest
import pyddl.pyddl as pdl

def test_state_eq_1():
    init_1 = (('at', 'a', 'b'))
    node_1 = pdl.State(predicates = init_1, functions={})

    init_2 = (('at', 'a', 'b'))
    node_2 = pdl.State(predicates = init_2, functions={})

    assert node_1 == node_2


def test_state_eq_2():
    init_1 = (('at', 'a', 'b'), ('at', 'c', 'd'))
    node_1 = pdl.State(predicates = init_1, functions={})

    init_2 = (('at', 'a', 'b'))
    node_2 = pdl.State(predicates = init_2, functions={})

    assert node_1 != node_2

def test_state_to_predicates():
    init = (('at', 'a', 'b'),)
    func = {'c': 3}
    node = pdl.State(predicates = init, functions=func)
    ret = node.to_predicates()

    assert ret == [('at', 'a', 'b'), ('=', 'c', 3)]



