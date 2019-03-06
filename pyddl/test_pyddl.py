

import pytest
from pyddl.pyddl import *

def test_action_init_1():
    with pytest.raises(Exception):

        Action(
            'Remove',
            parameters=(
                ('tire', 't'),
                ('location', 'l')
            ),
            preconditions=(
                ('at', 't', 'l')
            ),
            effects=(
                neg(('at', 't', 'l')),
                ('at', 't', 'ground'),
            ),
        )

def test_action_precondition_1():
    action = Action(
            'Remove',
            parameters=(
                ('tire', 't'),
                ('location', 'l')
            ),
            preconditions=(
                ('at', 't', 'l'),
            ),
            effects=(
                neg(('at', 't', 'l')),
                ('at', 't', 'ground'),
            ),
        )

    ground_precondition = action.ground('flat', 'ground').preconditions

    assert ground_precondition == [('at', 'flat', 'ground')]

def test_action_precondition_2():
    action = Action(
            'Remove',
            parameters=(
                ('tire', 't'),
                ('location', 'l')
            ),
            preconditions=(
                ('at', ('t', 't'), 'l'),
            ),
            effects=(
                neg(('at', 't', 'l')),
                ('at', 't', 'ground'),
            ),
        )

    ground_precondition = action.ground('flat', 'ground').preconditions

    assert ground_precondition == [('at', ('flat', 'flat'), 'ground')]

def test_action_precondition_3():
    action = Action(
            'Remove',
            parameters=(
                ('tire', 't'),
                ('location', 'l')
            ),
            preconditions=(
                ('at', 't', 'l'),
                ('<=', ('t', 'l'), 3)
            ),
            effects=(
                neg(('at', 't', 'l')),
                ('at', 't', 'ground'),
            ),
        )

    ground_precondition = action.ground('flat', 'ground').preconditions

    assert ground_precondition == [('at', 'flat', 'ground'), ('<=', ('flat', 'ground'), 3)]

def test_action_precondition_neg_1():
    action = Action(
            'Remove',
            parameters=(
                ('tire', 't'),
                ('location', 'l')
            ),
            preconditions=(
                neg(('at', 't', 'l')),
            ),
            effects=(
                neg(('at', 't', 'l')),
                ('at', 't', 'ground'),
            ),
        )

    ground_precondition = action.ground('flat', 'ground').preconditions

    assert ground_precondition == [(-1, ('at', 'flat', 'ground'))]

def test_action_init_2():
    with pytest.raises(Exception):

        Action(
            'Remove',
            parameters=(
                ('tire', 't'),
                ('location', 'l')
            ),
            preconditions=(
                ('at', 't', 'l')
            ),
            effects=(
                neg(('at', 't', 'l'))
            ),
        )

def test_action_effect_1():
    action = Action(
            'Remove',
            parameters=(
                ('tire', 't'),
                ('location', 'l')
            ),
            preconditions=(
                ('at', 't', 'l'),
            ),
            effects=(
                ('at', 't', 'l'),
            ),
        )

    ground_effect = action.ground('flat', 'ground').effects

    assert ground_effect == [('at', 'flat', 'ground')]

def test_action_effect_2():
    action = Action(
            'Remove',
            parameters=(
                ('tire', 't'),
                ('location', 'l')
            ),
            preconditions=(
                ('at', ('t', 't'), 'l'),
            ),
            effects=(
                ('at', ('t', 't'), 'l'),
            ),
        )

    ground_effects = action.ground('flat', 'ground').effects

    assert ground_effects == [('at', ('flat', 'flat'), 'ground')]

def test_action_effect_3():
    action = Action(
            'Remove',
            parameters=(
                ('tire', 't'),
                ('location', 'l')
            ),
            preconditions=(
                ('at', 't', 'l'),
                ('<=', ('t', 'l'), 3)
            ),
            effects=(
                ('at', 't', 'l'),
                ('<=', ('t', 'l'), 3)
            ),
        )

    ground_effects = action.ground('flat', 'ground').effects

    assert ground_effects == [('at', 'flat', 'ground'), ('<=', ('flat', 'ground'), 3)]

def test_action_effect_neg_1():
    action = Action(
            'Remove',
            parameters=(
                ('tire', 't'),
                ('location', 'l')
            ),
            preconditions=(
                neg(('at', 't', 'l')),
            ),
            effects=(
                neg(('at', 't', 'l')),
            ),
        )

    ground_effects = action.ground('flat', 'ground').effects

    assert ground_effects == [(-1, ('at', 'flat', 'ground'))]

def test_state_init_1():
    state = State((('at', 'a', 'b'),))
    assert state.predicates == frozenset((('at', 'a', 'b'),))

    state = State((('at', 'a', 'b'),('=', ('a',), 3)))
    assert state.predicates == frozenset((('at', 'a', 'b'), ('=', ('a',), 3)))

def test_state_apply_1():
    state = State((('at', 'a', 'b'),))

    action = Action(
            'test',
            effects=(
                ('at', 'c', 'd'),
            ),
        )
    ground_action = action.ground()
    new_state = state.apply(ground_action)

    assert new_state.predicates == frozenset((('at', 'a', 'b'), ('at', 'c', 'd')))

def test_state_apply_2():
    state = State((('=', 'a', 1),))

    action = Action(
            'test',
            effects=(
                ('+=', 'a', 1),
            ),
        )
    ground_action = action.ground()
    new_state = state.apply(ground_action)

    assert new_state.predicates == frozenset((('=', 'a', 2),))

def test_state_is_true_1():
    state = State((('at', 'a', 'b'),))
    predicates = (('at', 'a', 'b'),)
    ret = state.is_true(predicates)
    assert ret == True

    state = State((('at', 'a', 'b'),))
    predicates = (('at', 'a', 'c'),)
    ret = state.is_true(predicates)
    assert ret == False

def test_state_is_true_2():
    state = State((('=', 'a', 2),))
    predicates = (('<', 'a', 3),)
    ret = state.is_true(predicates)
    assert ret == True

    state = State((('=', 'a', 2),))
    predicates = (('<', 'a', 1),)
    ret = state.is_true(predicates)
    assert ret == False

def test_state_is_true_3():
    state = State((('at', 'a', 'b'), ('=', 'a', 2),))
    predicates = (('at', 'a', 'b'), ('<', 'a', 3),)
    ret = state.is_true(predicates)
    assert ret == True

    state = State((('at', 'a', 'b'), ('=', 'a', 2),))
    predicates = (('at', 'a', 'c'), ('<', 'a', 1),)
    ret = state.is_true(predicates)
    assert ret == False




