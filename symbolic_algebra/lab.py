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
        self.precedence = float('inf')

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
        self.precedence = float('inf')

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

def classname(val):
    return str(val.__class__.__name__)


class BinOp(Symbol):
    def __init__(self,left,right):
        true_vals = []
        for val in (left,right):
            if issubclass(val.__class__, Symbol):
                true_vals.append(val)
            elif isinstance(val,str):
                true_vals.append(Var(val))
            elif isinstance(val, int) or isinstance(val, float):
                true_vals.append(Num(val))
            else:
                raise TypeError
        op_dict = {
            "Add":('+',1,False),
            "Sub":('-',1,True),
            "Mul":('*',2,False),
            "Div":('/',2,True)            
        }
        self.operator, self.precedence, self.wrap_right_at_same_precedence=op_dict[classname(self)]
        self.left, self.right = true_vals
    
    def __repr__(self):
        operation = classname(self)
        return f"{operation}({repr(self.left)}, {repr(self.right)})"

    def __str__(self):
        if self.precedence > self.left.precedence:
            return f"({self.left}) {self.operator} {self.right}"
        elif self.precedence > self.right.precedence:
            return f"{self.left} {self.operator} ({self.right})"
        elif self.right.precedence == self.precedence and self.wrap_right_at_same_precedence:
            return f"{self.left} {self.operator} ({self.right})"
        else:
            return f"{self.left} {self.operator} {self.right}"

class Add(BinOp):
    ...
class Sub(BinOp):
    ...
class Mul(BinOp):
    ...
class Div(BinOp):
    ...


if __name__ == "__main__":
    doctest.testmod()
    z = Add(Var('x'), Sub(Var('y'), Num(2)))
    print(repr(z),z)
