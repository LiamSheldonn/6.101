# ALL_WORDS is a set containing all strings that should be considered valid
# words (all in lower-case)
with open('words.txt') as f:
    ALL_WORDS = {i.strip() for i in f}

# replace the following with the starting state
start_state = "fool"
alphabet = 'abcdefghijklmnopqrstuvwxyz'

# replace this neighbors function:
def word_ladder_neighbors(state):
    """
    takes a state as input
    returns all neighboring states (valid words that differ in one letter)
    """
    out = set()
    for i in range(len(state)):
        for letter in alphabet:
            test_word = state[:i]+letter+state[i+1:]
            if test_word in ALL_WORDS:
                out.add(test_word)
    return list(out)

# replace this goal test function:
def goal_test_function(state):
    """
    takes a state as input
    returns True if and only if state matches the goal (the target word)
    """
    return state == 'sage'

# ultimately, these variables will be passed as arguments to the find_path
# function to solve for the path between "patties" and "foaming"
#
#    output = find_path(word_ladder_neighbors, start_state, goal_test_function)
print(word_ladder_neighbors(start_state))