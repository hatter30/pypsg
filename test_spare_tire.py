#!/usr/bin/env python
"""
Example of using PyDDL to solve the "Missionaries and Cannibals" Problem.
A boat must transport a group of 3 missionaries and 3 cannibals across a river,
but at no time can the cannibals outnumber the missionaries at either side of
the river.
"""
from __future__ import print_function
from pyddl import Domain, Problem, Action, neg, planner

class PartialOrderPlanner:

    def __init__(self, planningproblem):
        self.problem = planningproblem
        self.initialize()

    def initialize(self):
        """Initialize all variables"""
        self.causal_links = []
        self.start = Action('Start', preconditions=(), effects=self.problem.init_predicates)
        self.finish = Action('Finish', preconditions=self.problem.goal_predicates, effects=())
        self.actions = set()
        self.actions.add(self.start)
        self.actions.add(self.finish)
        self.constraints = set()
        self.constraints.add((self.start, self.finish))
        self.agenda = set()
        for precond in self.finish.preconditions:
            self.agenda.add((precond, self.finish))
        self.expanded_actions = self.problem.grounded_actions

    def find_open_preconditions(self):
        pass

def problem():
    domain = Domain((
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
        ),
        Action(
            'PutOn',
            parameters=(
                ('tire', 't'),
            ),
            preconditions=(
                ('Tire', 't'),
                ('at', 't', 'ground'),
                neg(('at', 'flat', 'axle'))
            ),
            effects=(
                ('at', 't', 'axle'),
                neg(('at', 't', 'ground')),
            ),
        ),
        Action(
            'LeaveOvernight',
            parameters=(
            ),
            preconditions=(
            ),
            effects=(
                neg(('at', 'spare', 'ground')),
                neg(('at', 'spare', 'axle')),
                neg(('at', 'spare', 'trunk')),
                neg(('at', 'flat',  'ground')),
                neg(('at', 'flat',  'axle')),
                neg(('at', 'flat',  'trunk'))
            ),
        )
    ))
    problem = Problem(
        domain,
        {
            'tire': ('flat', 'spare'),
            'location': ('axle', 'Trunk', 'ground')
        },
        init=(
            ('Tire', 'flat'),
            ('Tire', 'spare'),
            ('at', 'flat', 'axle'),
            ('at', 'spare', 'trunk'),
        ),
        goal=(
            ('at', 'spare', 'axle'),
            ('at', 'flat', 'ground'),
        )
    )

    
    return problem

if __name__ == "__main__":
    st = problem()

    pop = PartialOrderPlanner(st)

    print(pop.agenda)
    print(pop.expanded_actions)


