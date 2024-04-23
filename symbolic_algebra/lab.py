"""
6.101 Lab:
Symbolic Algebra
"""

import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    """
    Overarching class for all symbols.
    """
    precedence = float("inf")

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)


class Var(Symbol):
    """
    Class to represent variables (str).
    """
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

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.name == other.name
        else:
            return False

    def deriv(self, var):
        return Num(1) if self.name == var else Num(0)

    def simplify(self):
        return self


class Num(Symbol):
    """
    Class to represent numbers (float or int).
    """
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

    def eval(self, _):
        return self.n

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.n == other.n
        else:
            return False

    def deriv(self, _):
        return Num(0)

    def simplify(self):
        return self


def classname(var):
    """
    Helper function to return the classname of any variable.
    """
    return str(var.__class__.__name__)


class BinOp(Symbol):
    """
    Class to represent all binary operations between two symbols.
    """
    def __init__(self, left, right):
        true_vals = []
        for val in (left, right):

            if issubclass(val.__class__, Symbol):
                true_vals.append(val)
            elif isinstance(val, str):
                true_vals.append(Var(val))
            elif isinstance(val, (float,int)):
                true_vals.append(Num(val))
            else:
                print(type(val))
                raise TypeError

        self.left, self.right = true_vals

    def __repr__(self):
        return f"{classname(self)}({repr(self.left)}, {repr(self.right)})"

    def __str__(self):
        left_part = (
            f"({self.left})"
            if self.precedence > self.left.precedence
            else f"{self.left}"
        )
        right_part = (
            f"({self.right})"
            if self.precedence > self.right.precedence
            or (
                self.right.precedence == self.precedence
                and self.wrap_right_at_same_precedence
            )
            else f"{self.right}"
        )
        return f"{left_part} {self.operator} {right_part}"

    def eval(self, mapping):
        left = self.left.eval(mapping)
        right = self.right.eval(mapping)
        return self.eval_helper(left, right)

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.right == other.right and self.left == other.left
        else:
            return False

    def simplify(self):
        left, right = self.left.simplify(), self.right.simplify()
        islnum = isinstance(left, Num)
        isrnum = isinstance(right, Num)
        if islnum and isrnum:
            return Num(self.eval_helper(left.n, right.n))
        else:
            return self.simp_helper(left, right)


class Add(BinOp):
    """
    Binary operation to represent addition.
    """
    operator = "+"
    precedence = 1
    wrap_right_at_same_precedence = False

    def eval_helper(self, left, right):
        return left + right

    def deriv(self, var):
        return Add(self.left.deriv(var), self.right.deriv(var))

    def simp_helper(self, left, right):
        if left == Num(0):
            return right
        elif right == Num(0):
            return left
        else:
            return Add(left, right)


class Sub(BinOp):
    """
    Binary operation to represent subtraction.
    """
    operator = "-"
    precedence = 1
    wrap_right_at_same_precedence = True

    def eval_helper(self, left, right):
        return left - right

    def deriv(self, var):
        return Sub(self.left.deriv(var), self.right.deriv(var))

    def simp_helper(self, left, right):
        if right == Num(0):
            return left
        else:
            return Sub(left, right)


class Mul(BinOp):
    """
    Binary operation to represent multiplication.
    """
    operator = "*"
    precedence = 2
    wrap_right_at_same_precedence = False

    def eval_helper(self, left, right):
        return left * right

    def deriv(self, var):
        return Add(
            Mul(self.left, self.right.deriv(var)), Mul(self.right, self.left.deriv(var))
        )

    def simp_helper(self, left, right):
        if left == Num(1):
            return right
        elif right == Num(1):
            return left
        elif left == Num(0) or right == Num(0):
            return Num(0)
        else:
            return Mul(left, right)


class Div(BinOp):
    """
    Binary operation to represent division.
    """
    operator = "/"
    precedence = 2
    wrap_right_at_same_precedence = True

    def eval_helper(self, left, right):
        return left / right

    def deriv(self, var):
        return Div(
            Sub(
                Mul(self.right, self.left.deriv(var)),
                Mul(self.left, self.right.deriv(var)),
            ),
            Mul(self.right, self.right),
        )

    def simp_helper(self, left, right):
        if left == Num(0):
            return Num(0)
        elif right == Num(1):
            return left
        else:
            return Div(left, right)


def type_of_char(prev, char):
    """
    Helper function that determines the type of a given character.
    """
    if char in "()":
        return "p"
    elif char in "+*/":
        return "op"
    elif char == "-":
        if prev == "":
            return "n"
        elif prev[-1] in "+-*/(":
            return "n"
        else:
            return "op"
    elif char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        return "v"
    else:
        return "n"


def tokenize(exp):
    """
    Function to split a string expression into tokens.
    """

    tokens = []
    new_exp = exp.replace(" ", "")
    current_type = type_of_char("", new_exp[0])
    current_token = new_exp[0]
    for i, char in enumerate(new_exp[1:]):
        next_type = type_of_char(new_exp[i], char)
        if current_type == next_type and next_type != "p":
            current_token += char
        else:
            tokens.append(current_token)
            current_token = char
        current_type = next_type
    tokens.append(current_token)
    return tokens


def parse(tokens):
    """
    Function to parse a list of tokens into a BinOp expression.
    """
    op_dict = {"+": Add, "-": Sub, "*": Mul, "/": Div}

    def parse_expression(index):
        curval = tokens[index]
        curtype = type_of_char("00", curval)
        print(curval)
        if curtype == "n":
            out = Num(float(curval)) if "." in curval else Num(int(curval))
            return (out, index + 1)
        if curtype == "v":
            return (Var(curval), index + 1)
        else:
            e1, n1 = parse_expression(index + 1)
            op = tokens[n1]
            e2, n2 = parse_expression(n1 + 1)
            return (op_dict[op](e1, e2), n2 + 1)

    parsed_expression, _ = parse_expression(0)
    return parsed_expression


def expression(exp):
    """
    Function to turn a string expression into a BinOp expression.
    """
    tokens = tokenize(exp)
    return parse(tokens)


if __name__ == "__main__":
    doctest.testmod()
    x = Var("x")
    y = Var("y")
    z = 2 * x - x * y + 3 * y
    # print(z.deriv('y').simplify())
