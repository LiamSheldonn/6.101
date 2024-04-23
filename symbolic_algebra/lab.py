"""
6.101 Lab:
Symbolic Algebra
"""

import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    precedence = float("inf")

    def __add__(self, other):
        return Add(self,other)

    def __radd__(self,other):
        return Add(other,self)

    def __sub__(self, other):
        return Sub(self,other)

    def __rsub__(self,other):
        return Sub(other,self)

    def __mul__(self, other):
        return Mul(self,other)

    def __rmul__(self,other):
        return Mul(other,self)

    def __truediv__(self, other):
        return Div(self,other)
    def __rtruediv__(self,other):
        return Div(other,self)


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
    
    def eval(self, mapping):
        if self.name in mapping:
            return mapping[self.name]
        else:
            raise NameError
    def __eq__(self,other):
        if self.__class__ == other.__class__:
            return self.name == other.name
        else:
            return False

    def deriv(self,var):
        return Num(1) if self.name == var else Num(0)

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
    
    def eval(self,_):
        return self.n
    
    def __eq__(self,other):
        if self.__class__ == other.__class__:
            return self.n == other.n
        else:
            return False
    
    def deriv(self,var):
        return Num(0)

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
        
        self.left, self.right = true_vals

    def __repr__(self):
        return f"{classname(self)}({repr(self.left)}, {repr(self.right)})"

    def __str__(self):
        if self.precedence > self.left.precedence:
            return f"({self.left}) {self.operator} {self.right}"
        elif self.precedence > self.right.precedence:
            return f"{self.left} {self.operator} ({self.right})"
        elif self.right.precedence == self.precedence and self.wrap_right_at_same_precedence:
            return f"{self.left} {self.operator} ({self.right})"
        else:
            return f"{self.left} {self.operator} {self.right}"

    def eval(self, mapping):
        left = self.left.eval(mapping)
        right = self.right.eval(mapping)
        return self.eval_helper(left,right)

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.right == other.right and self.left == other.left
        else:
            return False  
    

    
    
class Add(BinOp):
    operator = '+'
    precedence = 1
    wrap_right_at_same_precedence = False
    def eval_helper(self,l,r):
        return l+r
    def deriv(self,var):
        return Add(self.left.deriv(var),self.right.deriv(var))        
class Sub(BinOp):
    operator = '-'
    precedence = 1
    wrap_right_at_same_precedence = True
    def eval_helper(self,l,r):
        return l-r
    def deriv(self,var):
        return Sub(self.left.deriv(var),self.right.deriv(var))

class Mul(BinOp):
    operator = '*'
    precedence = 2
    wrap_right_at_same_precedence = False
    def eval_helper(self,l,r):
        return l*r
    def deriv(self,var):
        return Add(Mul(self.left,self.right.deriv(var)),Mul(self.right,self.left.deriv(var)))

class Div(BinOp):
    operator = '/'
    precedence = 2
    wrap_right_at_same_precedence = True
    def eval_helper(self,l,r):
        return l/r
    def deriv(self,var):
        return Div(Sub(Mul(self.right,self.left.deriv(var)),Mul(self.left,self.right.deriv(var))),Mul(self.right,self.right))


if __name__ == "__main__":
    doctest.testmod()
    x = Var('x')
    y = Var('y')
    z = 2*x - x*y + 3*y
    print(z.deriv('x'))
