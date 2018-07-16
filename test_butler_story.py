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
                ('owner', 'from'),
                ('object', 'obj'),
                ('target', 'to'),
            ),
            preconditions=(
                ('have', 'from', 'obj'),
            ),
            effects=(
                neg(('have', 'from', 'obj')),
                ('have', 'to', 'obj'),
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

    plan = planner(problem, verbose=verbose)
    if plan is None:
        print('No Plan!')
    else:
        for action in plan:
            print(action)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option('-q', '--quiet',
                      action='store_false', dest='verbose', default=True,
                      help="don't print statistics to stdout")

    # Parse arguments
    opts, args = parser.parse_args()
    problem(opts.verbose)
