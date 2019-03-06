"""
code based on : https://github.com/garydoranjr/pyddl

Classes and functions that allow creating a PDDL-like
problem and domain definition for planning
"""
from itertools import product
import operator as ops
import copy

NUM_OPS = {
    '>' : ops.gt,
    '<' : ops.lt,
    '=' : ops.eq,
    '>=': ops.ge,
    '<=': ops.le,
    '==': ops.is_,
    '!=': ops.is_not
}

class Domain(object):

    def __init__(self, actions=()):
        """
        Represents a PDDL-like Problem Domain
        @arg actions : list of Action objects
        """
        self.actions = tuple(actions)

    def ground(self, objects):
        """
        Ground all action schemas given a dictionary
        of objects keyed by type
        """
        grounded_actions = list()
        for action in self.actions:
            param_lists = [objects[t] for t in action.types]
            param_combos = set()
            for params in product(*param_lists):
                param_set = frozenset(params)
                if action.unique and len(param_set) != len(params):
                    continue
                if action.no_permute and param_set in param_combos:
                    continue
                param_combos.add(param_set)
                grounded_actions.append(action.ground(*params))
        return grounded_actions

class Problem(object):

    def __init__(self, domain, objects, init=(), goal=()):
        """
        Represents a PDDL Problem Specification
        @arg domain : Domain object specifying domain
        @arg objects : dictionary of object tuples keyed by type
        @arg init : tuple of initial state predicates
        @arg goal : tuple of goal state predicates
        """
        # Ground actions from domain
        self.grounded_actions = domain.ground(objects)

        self.init = init 
        self.goal = goal

    def initial_state(self):
        return State(self.init)

class State(object):

    def __init__(self, predicates, cost=0, predecessor=None):
        """Represents a state for A* search"""
        self.predicates = frozenset(predicates)
        self.predecessor = predecessor
        self.cost = cost

    def is_true(self, preconditions):
        preds = set([pre for pre in self.predicates if pre[0] != "="])
        num_preds = set(self.predicates) - preds
        functions = {func: num for _, func, num in num_preds}

        def _num_pred(op, x, y):
            operands = [0, 0]
            for i, o in enumerate((x, y)):
                if type(o) == int:
                    operands[i] = o
                else:
                    operands[i] = functions.get(o, o)
            return NUM_OPS[op](*operands)

        preconds = [precond for precond in preconditions if precond[0] not in NUM_OPS]
        num_preconds = [_num_pred(*precond) for precond in preconditions if precond[0] in NUM_OPS]

        return all(p in preds for p in preconds) and all(p for p in num_preconds)

    def apply(self, action, monotone=False):
        """
        Apply the action to this state to produce a new state.
        If monotone, ignore the delete list (for A* heuristic)
        """
        new_preds = set([pre for pre in self.predicates if pre[0] != "="])
        num_preds = set(self.predicates) - new_preds
        new_functions = {func: num for _, func, num in num_preds}

        add_effects = [effect for effect in action.effects if effect[0] not in [-1, "+=", "-="]]
        del_effects =   [effect[1] for effect in action.effects if effect[0] == -1]
        num_effects =   [(effect[1], effect[2]) for effect in action.effects if effect[0] == "+="] +\
                        [(effect[1], -effect[2]) for effect in action.effects if effect[0] == "-="]

        assert len(action.effects) == len(add_effects + del_effects + num_effects)
        
        new_preds |= set(add_effects)
        if not monotone:
            new_preds -= set(del_effects)
        for function, value in num_effects:
            new_functions[function] += value
        new_preds |= set(('=', function, value) for function, value in new_functions.items())

        return State(new_preds, self.cost + 1, (self, action))

    def plan(self):
        """
        Follow backpointers to successor states
        to produce a plan.
        """
        plan = list()
        n = self
        while n.predecessor is not None:
            plan.append(n.predecessor[1])
            n = n.predecessor[0]
        plan.reverse()
        return plan

    # Implement __hash__ and __eq__ so we can easily
    # check if we've encountered this state before

    def __hash__(self):
        return hash(self.predicates)

    def __eq__(self, other):
        return self.predicates == other.predicates

    def __str__(self):
        return 'Predicates:\n%s' % '\n'.join(map(str, self.predicates))

    def __lt__(self, other):
        return hash(self) < hash(other)

def neg(effect):
    """
    Makes the given effect a negative (delete) effect, like 'not' in PDDL.
    """
    return (-1, effect)

class Action(object):
    """
    An action schema
    """
    def __init__(self, name, parameters=(), preconditions=(), effects=(),
                 unique=False, no_permute=False):
        """
        A PDDL-like action schema
        @arg name : action name for display purposes
        @arg parameters : tuple of ('type', 'param_name') tuples indicating
                          action parameters
        @arg precondtions : tuple of preconditions for the action
        @arg effects : tuple of effects of the action
        @arg unique : if True, only ground with unique arguments (no duplicates)
        @arg no_permute : if True, do not ground an action twice with the same
                          set of (permuted) arguments
        """
        self.name = name
        if len(parameters) > 0 and isinstance(parameters[0], tuple):
            self.types, self.arg_names = zip(*parameters)
        elif len(parameters) > 0:
            raise Exception("Invalid parameters")
        else:
            self.types = tuple()
            self.arg_names = tuple()

        if len(preconditions) > 0 and not isinstance(preconditions[0], tuple):
            raise Exception("Invalid preconditions")
        else:
            self.preconditions = preconditions

        if len(effects) > 0 and not isinstance(effects[0], tuple):
            raise Exception("Invalid effects")
        else:
            self.effects = effects        
        
        self.unique = unique
        self.no_permute = no_permute

    def ground(self, *args):
        return _GroundedAction(self, *args)

    def __str__(self):
        arglist = ', '.join(['%s - %s' % pair for pair in zip(self.arg_names, self.types)])
        return '%s(%s)' % (self.name, arglist)

    def __repr__(self):
        arglist = ', '.join(['%s - %s' % pair for pair in zip(self.arg_names, self.types)])
        return '%s(%s)' % (self.name, arglist)

def _grounder(arg_names, args):
    """
    Returns a function for grounding predicates and function symbols
    """
    namemap = dict()
    for arg_name, arg in zip(arg_names, args):
        namemap[arg_name] = arg
    def _ground_by_names(predicate):
        if isinstance(predicate, tuple):
            return tuple(namemap.get(arg, _ground_by_names(arg)) for arg in predicate)
        elif isinstance(predicate, str) or isinstance(predicate, int):
            return namemap.get(predicate, predicate)
        else:
            raise Exception(f"Invalid Case predicate type : {type(predicate)}")
    return _ground_by_names

class _GroundedAction(object):
    """
    An action schema that has been grounded with objects
    """
    def __init__(self, action, *args):
        self.name = action.name
        ground = _grounder(action.arg_names, args)

        # Ground Action Signature
        self.sig = ground((self.name,) + action.arg_names)

        # Ground Preconditions, Effects
        self.preconditions = [ground(pre) for pre in action.preconditions]
        self.effects = [ground(effect) for effect in action.effects]

    def __str__(self):
        arglist = ', '.join(map(str, self.sig[1:]))
        return '%s(%s)' % (self.sig[0], arglist)

    def __repr__(self):
        arglist = ', '.join(map(str, self.sig[1:]))
        return '%s(%s)' % (self.sig[0], arglist)
