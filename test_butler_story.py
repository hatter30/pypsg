#!/usr/bin/env python
"""
Example of using PyDDL to solve the "Missionaries and Cannibals" Problem.
A boat must transport a group of 3 missionaries and 3 cannibals across a river,
but at no time can the cannibals outnumber the missionaries at either side of
the river.
"""
from __future__ import print_function
from pyddl import Domain, Problem, Action, neg, planner

def problem(verbose):
    domain = Domain((
        Action(
            'Put-poison',
            parameters=(
                ('owner', 'o'),
            ),
            preconditions=(
                ('have', 'o', 'poison'),
                ('have', 'o', 'wine'),
            ),
            effects=(
                neg(('have', 'o', 'poison')),
                ('poisoned', 'wine'),
            ),
        ),
        Action(
            'Carry',
            parameters=(
                ('owner', 'o'),
                ('object', 'obj'),
                ('target', 't'),
            ),
            preconditions=(
                ('have', 'o', 'obj'),
            ),
            effects=(
                neg(('have', 'o', 'obj')),
                ('have', 't', 'obj'),
            ),
        ),
        Action(
            'Drink',
            parameters=(
                ('owner', 'o'),
                ('object', 'obj'),
            ),
            preconditions=(
                ('have', 'o', 'obj'),
            ),
            effects=(
                neg(('have', 'o', 'obj')),
                ('drinking', 'o', 'obj'),
            ),
        ),
        Action(
            'Fall-down',
            parameters=(
                ('owner', 'o'),
                ('object', 'obj'),
            ),
            preconditions=(
                ('drinking', 'o', 'obj'),
                ('poisoned', 'obj')
            ),
            effects=(
                ('dead', 'o'),
            ),
        ),
    ))
    problem = Problem(
        domain,
        {
            'owner': ('butler', 'lord'),
            'target': ('butler', 'lord'),
            'object': ('wine', 'poison'),
        },
        init=(
            ('have', 'butler', 'poison'),
            ('have', 'butler', 'wine')
        ),
        goal=(
            ('dead', 'lord'),
        )
    )

    print('===== initial state =====')
    node = problem.initial_state
    print(node)

    print('===== grounded action=====')
    for grounded_action in problem.grounded_actions:
        print(grounded_action)
        print('- precondition -')
        print(grounded_action.preconditions)
        print('- numerical_precondition -')
        print(grounded_action.num_preconditions)

        print('next state')
        if node.is_true(grounded_action.preconditions, grounded_action.num_preconditions):

            next_state = node.apply(grounded_action, monotone=False)
            print(next_state)

        print('---- end of action ----\n')

    print('===== End =====')


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option('-q', '--quiet',
                      action='store_false', dest='verbose', default=True,
                      help="don't print statistics to stdout")

    # Parse arguments
    opts, args = parser.parse_args()
    problem(opts.verbose)
