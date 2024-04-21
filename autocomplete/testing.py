from lab import PrefixTree
from lab import word_frequencies, autocomplete

t = PrefixTree()
t['bat'] = 2
t['bar'] = 1
t['bark'] = 1
# print(autocomplete(t, 'ba',1))
# print(autocomplete(t, "ba", 2))
# print(autocomplete(t, "be", 2))
# print(autocomplete(t, 'ba'))


nt = t.get('children')['b']
print(nt['at'])