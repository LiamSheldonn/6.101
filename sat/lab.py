"""
6.101 Lab:
SAT Solver
"""

#!/usr/bin/env python3

import sys
import typing

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS


def update_formula(formula, var, val):
    """
    Updates a CNF Formula by setting var to val.
    """
    out = []
    for clause in formula:
        newclause = []
        append = True
        for literal in clause:
            if literal[0] == var:
                if literal[1] != val:
                    continue
                else:
                    append = False
                break
            else:
                newclause.append(literal)
        if append:
            out.append(newclause)
    return out


def satisfying_assignment(formula, all_vars=None):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    if [] in formula:
        return None

    if formula == []:
        return {}

    if not all_vars:
        all_vars = set(var for clause in formula for var, _ in clause)

    
    def find_onelengths(formula):
        for clause in formula:
            if len(clause) == 1:
                return clause[0]
        return None

    def find_assignment(formula, used):
        if len(used) == 1:
            var = next(iter(used))
            val = used[var]
            new_formula = update_formula(formula, var, val)
        else:
            new_formula = formula
        new_solution = satisfying_assignment(new_formula, all_vars - set(used.keys()))
        if new_solution is not None:
            return new_solution | used
        else:
            return None

    onelength = find_onelengths(formula)
    if onelength:
        new_formula = formula
        used = {}
        while onelength:
            var, val = onelength#[0]
            used[var] = val
            new_formula = update_formula(new_formula, var, val)
            if [] in new_formula:
                return None
            if new_formula == []:
                return used
            onelength = find_onelengths(new_formula)
        return find_assignment(new_formula, used)

    for var in all_vars:
        for val in (True,False):
            new_assignment = find_assignment(formula,{var:val})
            if new_assignment is not None:
                return new_assignment
        return None

    return None


def all_n_lengths(collection, n):
    """
    Returns all combinations of length n from a collection.
    """

    if n == 0:
        return [()]
    if not collection:
        return []
    first = collection[0]
    rest = collection[1:]
    rest_smaller_combos = all_n_lengths(rest, n - 1)
    first_combos = [(first,) + item for item in rest_smaller_combos]

    rest_combos = all_n_lengths(rest, n)

    return first_combos + rest_combos


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """

    def possibilities(pair_type):
        assert (
            pair_type in {'student','room'}
        ), "Must be either room or student!"
        out = []
        possibility_list = list(
            room_capacities.keys()
            if pair_type == "student"
            else student_preferences.keys()
        )
        pairing_dict = (
            student_preferences if pair_type == "student" else room_capacities
        )
        for key, val in pairing_dict.items():
            for combo in all_n_lengths(
                possibility_list, 2 if pair_type == "student" else val + 1
            ):
                out.append(
                    [
                        (
                            (
                                key + "_" + item
                                if pair_type == "student"
                                else item + "_" + key
                            ),
                            False,
                        )
                        for item in combo
                    ]
                )
        return out

    out = []
    for person, preferences in student_preferences.items():
        out.append([(person + "_" + room, True) for room in preferences])
    out += possibilities("student")
    out += possibilities("room")
    return out


if __name__ == "__main__":
    import doctest

    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
