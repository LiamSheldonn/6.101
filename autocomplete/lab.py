"""
6.101 Lab:
Autocomplete
"""

# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    """
    Tree representing a dictionary with strings as keys.
    """

    def __init__(self):
        self.value = None
        self.children = {}

    def get(self, thing):
        """
        Gets either the value or the children of a prefixtree
        """
        return (
            self.value
            if thing == "value"
            else self.children if thing == "children" else None
        )

    def set_children(self, k, v):
        """
        Sets the children of a prefixtree
        """
        self.children[k] = v

    def set_value(self, val):
        """
        Sets the value of a prefixtree
        """
        self.value = val

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError

        current = self
        for letter in key:
            if letter not in current.children:
                current.children[letter] = PrefixTree()
            current = current.children[letter]
        current.value = value

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError

        current = self
        for letter in key:
            if letter not in current.children:
                raise KeyError
            current = current.children[letter]
        return current.value

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError

        if key not in self:
            raise KeyError

        self[key] = None

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError

        current = self
        for letter in key:
            if letter not in current.children:
                return False
            current = current.children[letter]
        return bool(current.value is not None)

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """

        def recursive_helper(tree, path=""):
            """
            Recursive helper to iterate deeper and deeper.
            """
            for letter, subtree in tree.children.items():
                val = subtree.value
                if val is not None:
                    yield (path + letter, val)
                yield from recursive_helper(subtree, path + letter)

        yield from recursive_helper(self)

    def increment(self, key, i):
        """
        Increment the value at key by i.
        """
        if not isinstance(key, str):
            raise TypeError

        current = self
        for letter in key:
            if letter not in current.children:
                current.children[letter] = PrefixTree()
            current = current.children[letter]
        if current.value is None:
            current.value = 0
        current.value += i


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    tree = PrefixTree()
    words = [
        word for sentence in tokenize_sentences(text) for word in sentence.split(" ")
    ]
    for word in words:
        tree.increment(word, 1)
    return tree


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError

    current = tree
    for letter in prefix:
        if letter not in current.get("children"):
            return []
        current = current.get("children")[letter]
    nexts = dict(current)
    if current.get("value") is not None:
        nexts[""] = current.get("value")
    if max_count is None:
        max_count = float("inf")
    out = []
    for _ in range(min(max_count, len(nexts))):
        out.append(prefix + (curmax := max(nexts, key=nexts.get)))
        del nexts[curmax]
    return out


alphabet = "abcdefghijklmnopqrstuvwxyz"


def edit_dict(tree, word):
    """
    Produces a dictionary of all possible edits of a word 
    and their frequencies, if in the tree.
    """
    out = {}
    for i,_ in enumerate(word):
        delete = word[:i] + word[i + 1 :]
        if delete in tree:
            out[delete] = tree[delete]
        if i < len(word) - 1:
            swap = word[:i] + word[i + 1] + word[i] + word[i + 2 :]
            if swap in tree:
                out[swap] = tree[swap]
        for letter in alphabet:
            edits = (word[:i] + letter + word[i + 1 :], word[:i] + letter + word[i:])
            for edit in edits:
                if edit in tree:
                    out[edit] = tree[edit]
    return out


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    completed = set(autocomplete(tree, prefix, max_count))
    left = max_count - len(completed) if max_count is not None else float("inf")
    edits = edit_dict(tree, prefix)
    edits_left = min(left, len(edits))
    while edits_left > 0:
        previous_len = len(completed)
        completed.add(curmax := max(edits, key=edits.get))
        new_len = len(completed)
        del edits[curmax]
        if new_len>previous_len:
            edits_left -= 1
    return list(completed)


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """

    out = set()

    def recursive_helper(tree, pattern, path=""):
        if pattern:
            first, rest = pattern[0], pattern[1:]
            children = tree.get("children")
            if first in children:
                recursive_helper(children[first], rest, path + first)
            elif first == "?":
                for child in children:
                    recursive_helper(children[child], rest, path + child)
            elif first == "*":
                recursive_helper(tree, rest, path)
                for child in children:
                    recursive_helper(children[child], pattern, path + child)
        elif (value := tree.get("value")) is not None:
            out.add((path, value))

    recursive_helper(tree, pattern)
    return list(out)


# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
    with open("dracula.txt", encoding="utf-8") as f:
        text = f.read()
    texttree = word_frequencies(text)
    print(len(list(texttree)))
    print(sum([val for _,val in texttree]))