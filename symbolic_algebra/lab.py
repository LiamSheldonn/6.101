"""
6.101 Lab:
Symbolic Algebra
"""

import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    pass


class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"


class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

class BinOp():
    def __init__(self,left,right):
        true_vals = []
        for val in (left,right):
            if isinstance(val, Var) or isinstance(val, Num):
                true_vals.append(val)
            elif isinstance(val,str):
                true_vals.append(Var(val))
            elif isinstance(val, int) or isinstance(val, float):
                true_vals.append(Num(val))
            else:
                raise TypeError
        self.left, self.right = true_vals
    
    def represent(self, operator):
        return f"{operator}({repr(self.left)}, {repr(self.right)})"
    def string(self, operator):
        return f"{self.left} {operator} {self.right}"

class Add(BinOp):
    def __repr__(self):
        return self.represent("Add")
    def __str__(self):
        return self.string('+')

class Sub(BinOp):
    def __repr__(self):
        return self.represent("Sub")
    def __str__(self):
        return self.string('-')

class Mul(BinOp):
    def __repr__(self):
        return self.represent("Mul")
    def __str__(self):
        return self.string('*')
class Div(BinOp):
    def __repr__(self):
        return self.represent("Div")
    def __str__(self):
        return self.string('/')


if __name__ == "__main__":
    doctest.testmod()
    z = Add(Var('x'), Sub(Var('y'), Num(2)))
    print(repr(z),z)
