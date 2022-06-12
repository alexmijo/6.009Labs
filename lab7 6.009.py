import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    precedence = float('inf') # By default, Symbols have infinite precedence in PEMDAS

    def ensure_Symbol(self, obj):
        """
        obj can be a string, integer or Symbol. Will return the Symbol version of obj (int
        becomes Num, string becomes Var, Symbols are simply returned).
        """
        # Strings are turned into Vars
        if type(obj) == type(str()):
            return Var(obj)
        # Ints are turned into Nums
        elif type(obj) == type(int()):
            return Num(obj)
        # Symbols are returned as is
        else:
            return obj

    def __add__(self, rightSymbol):
        return Add(self, self.ensure_Symbol(rightSymbol))

    def __radd__(self, leftSymbol):
        return Add(self.ensure_Symbol(leftSymbol), self)

    def __sub__(self, rightSymbol):
        return Sub(self, self.ensure_Symbol(rightSymbol))

    def __rsub__(self, leftSymbol):
        return Sub(self.ensure_Symbol(leftSymbol), self)

    def __mul__(self, rightSymbol):
        return Mul(self, self.ensure_Symbol(rightSymbol))

    def __rmul__(self, leftSymbol):
        return Mul(self.ensure_Symbol(leftSymbol), self)

    def __truediv__(self, rightSymbol):
        return Div(self, self.ensure_Symbol(rightSymbol))

    def __rtruediv__(self, leftSymbol):
        return Div(self.ensure_Symbol(leftSymbol), self)

    def simplify(self):
        return self # By default, a Symbol simplifies to itself


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
        return 'Var(' + repr(self.name) + ')'

    def deriv(self, withRespectTo):
        if withRespectTo == self.name:
            return Num(1)
        return Num(0)

    def eval(self, mapping):
        if self.name not in mapping:
            raise ValueError(self.name + ' not in mapping')
        return mapping[self.name]


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
        return 'Num(' + repr(self.n) + ')'

    def deriv(self, withRespectTo):
        return Num(0)

    def get_value(self):
        return self.n

    def eval(self, mapping):
        return self.n


class BinOp(Symbol):
    def __init__(self, left, right):
        """
        Initializer. Stores instance variables `left` and `right`, containing the instance's
        lefthand and righthand operands as Symbol instances. Also accepts integers or
        strings as arguments, which will be turned into Nums or Vars respectively before
        being stored as `left` and `right`.
        """
        self.left = self.ensure_Symbol(left)
        self.right = self.ensure_Symbol(right)

    def parenthesize_if_needed(self, wantLeftOperand):
        """
        Returns a correctly parenthesized string version of self.left if wantLeftOperand is
        True, or of self.right if wantLeftOperand is False.
        """
        if wantLeftOperand:
            if self.precedence > self.left.precedence:
                return '(' + str(self.left) + ')'
            return str(self.left)
        # Special case for subtraction and division with right operand
        if self.precedence > self.right.precedence or\
           (self.operator in ('-', '/') and self.precedence == self.right.precedence):
            return '(' + str(self.right) + ')'
        return str(self.right)

    def __str__(self):
        return self.parenthesize_if_needed(True) + ' ' + self.operator + ' ' +\
               self.parenthesize_if_needed(False)

    def __repr__(self):
        return self.reprName + '(' + repr(self.left) + ', ' + repr(self.right) + ')'


class Add(BinOp):
    operator = '+'
    precedence = 0 # Level of precedence in PEMDAS
    reprName = 'Add'

    def deriv(self, withRespectTo):
        return Add(self.left.deriv(withRespectTo), self.right.deriv(withRespectTo))

    def simplify(self):
        simplifiedLeft = self.left.simplify()
        simplifiedRight = self.right.simplify()
        if isinstance(simplifiedLeft, Num):
            if isinstance(simplifiedRight, Num):
                # Any binary operation on two numbers should simplify to a single number
                # containing the result
                return Num(simplifiedLeft.get_value() + simplifiedRight.get_value())
            if simplifiedLeft.get_value() == 0:
                # Adding 0 to any expression E should simplify to E
                return simplifiedRight
        if isinstance(simplifiedRight, Num) and simplifiedRight.get_value() == 0:
            # Adding 0 to any expression E should simplify to E
            return simplifiedLeft
        return Add(simplifiedLeft, simplifiedRight)

    def eval(self, mapping):
        evaluatedLeft = self.left.eval(mapping)
        evaluatedRight = self.right.eval(mapping)
        return evaluatedLeft + evaluatedRight


class Sub(BinOp):
    operator = '-'
    precedence = 0 # Level of precedence in PEMDAS
    reprName = 'Sub'

    def deriv(self, withRespectTo):
        return Sub(self.left.deriv(withRespectTo), self.right.deriv(withRespectTo))

    def simplify(self):
        simplifiedLeft = self.left.simplify()
        simplifiedRight = self.right.simplify()
        if isinstance(simplifiedRight, Num):
            if isinstance(simplifiedLeft, Num):
                # Any binary operation on two numbers should simplify to a single number
                # containing the result
                return Num(simplifiedLeft.get_value() - simplifiedRight.get_value())
            if simplifiedRight.get_value() == 0:
                # Subtracting 0 from any expression E should simplify to E
                return simplifiedLeft
        return Sub(simplifiedLeft, simplifiedRight)

    def eval(self, mapping):
        evaluatedLeft = self.left.eval(mapping)
        evaluatedRight = self.right.eval(mapping)
        return evaluatedLeft - evaluatedRight


class Mul(BinOp):
    operator = '*'
    precedence = 1 # Level of precedence in PEMDAS
    reprName = 'Mul'

    def deriv(self, withRespectTo):
        # Use multiplication rule for partial derivatives
        firstPart = Mul(self.left, self.right.deriv(withRespectTo))
        secondPart = Mul(self.right, self.left.deriv(withRespectTo))
        return Add(firstPart, secondPart)

    def simplify(self):
        simplifiedLeft = self.left.simplify()
        simplifiedRight = self.right.simplify()
        if isinstance(simplifiedLeft, Num):
            if isinstance(simplifiedRight, Num):
                # Any binary operation on two numbers should simplify to a single number
                # containing the result
                return Num(simplifiedLeft.get_value() * simplifiedRight.get_value())
            if simplifiedLeft.get_value() == 0:
                # Multiplying any expression E by 0 should simplify to 0
                return Num(0)
            if simplifiedLeft.get_value() == 1:
                # Multiplying any expression E by 1 should simplify to E
                return simplifiedRight
        if isinstance(simplifiedRight, Num):
            if simplifiedRight.get_value() == 0:
                # Multiplying any expression E by 0 should simplify to 0
                return Num(0)
            if simplifiedRight.get_value() == 1:
                # Multiplying any expression E by 1 should simplify to E
                return simplifiedLeft
        return Mul(simplifiedLeft, simplifiedRight)

    def eval(self, mapping):
        evaluatedLeft = self.left.eval(mapping)
        evaluatedRight = self.right.eval(mapping)
        return evaluatedLeft * evaluatedRight


class Div(BinOp):
    operator = '/'
    precedence = 1 # Level of precedence in PEMDAS
    reprName = 'Div'
    
    def deriv(self, withRespectTo):
        # Use division rule for partial derivatives
        firstPart = Mul(self.right, self.left.deriv(withRespectTo))
        secondPart = Mul(self.left, self.right.deriv(withRespectTo))
        numerator = Sub(firstPart, secondPart)
        denominator = Mul(self.right, self.right)
        return Div(numerator, denominator)

    def simplify(self):
        simplifiedLeft = self.left.simplify()
        simplifiedRight = self.right.simplify()
        if isinstance(simplifiedLeft, Num):
            if isinstance(simplifiedRight, Num):
                # Any binary operation on two numbers should simplify to a single number
                # containing the result
                return Num(simplifiedLeft.get_value() / simplifiedRight.get_value())
            if simplifiedLeft.get_value() == 0:
                # Dividing 0 by any expression should simplify to 0
                return Num(0)
        if isinstance(simplifiedRight, Num) and simplifiedRight.get_value() == 1:
                # Dividing any expression E by 1 should simplify to E
                return simplifiedLeft
        return Div(simplifiedLeft, simplifiedRight)

    def eval(self, mapping):
        evaluatedLeft = self.left.eval(mapping)
        evaluatedRight = self.right.eval(mapping)
        return evaluatedLeft / evaluatedRight


def sym(expression):
    """
    Parses a string (expression) into a Symbol, which is then returned.
    """
    tokens = tokenize(expression)
    return parse(tokens)


def tokenize(expression):
    """
    Tokenizes a string (expression) into a list of tokens (parentheses, variable names,
    numbers, or operands), which is then returned.
    """
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    tokens = []
    idx = 0
    while idx < len(expression):
        if expression[idx] in ('(', ')', '+', '*', '/') or expression[idx] in letters:
            tokens.append(expression[idx])
        elif expression[idx] == '-':
            # expression will never end with a '-', so no index error
            if expression[idx + 1] == ' ':
                tokens.append(expression[idx])
            # Must handle negative numbers
            else:
                endOfNumber = idx + 1
                while endOfNumber < len(expression):
                    if expression[endOfNumber] in (' ', ')'):
                        break
                    endOfNumber += 1
                tokens.append(int(expression[idx:endOfNumber]))
                idx = endOfNumber
                continue
        # Must handle positive numbers
        elif expression[idx] != ' ':
            endOfNumber = idx + 1
            while endOfNumber < len(expression):
                if expression[endOfNumber] in (' ', ')'):
                    break
                endOfNumber += 1
            tokens.append(int(expression[idx:endOfNumber]))
            idx = endOfNumber
            continue
        idx += 1
    return tokens


def parse(tokens):
    """
    Turns tokens, a list of tokens (parentheses, variable names, numbers, or operands), into
    the corresponding Symbol, which is then returned.
    """
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    
    def parse_expression(idx):
        # Variable
        if tokens[idx] in letters:
            return (Var(tokens[idx]), idx + 1)
        # Operation
        if tokens[idx] == '(':
            leftOperand, endOfLeftOperand = parse_expression(idx + 1)
            rightOperand, endOfRightOperand = parse_expression(endOfLeftOperand + 1)
            if tokens[endOfLeftOperand] == '+':
                return (Add(leftOperand, rightOperand), endOfRightOperand + 1)
            if tokens[endOfLeftOperand] == '-':
                return (Sub(leftOperand, rightOperand), endOfRightOperand + 1)
            if tokens[endOfLeftOperand] == '*':
                return (Mul(leftOperand, rightOperand), endOfRightOperand + 1)
            if tokens[endOfLeftOperand] == '/':
                return (Div(leftOperand, rightOperand), endOfRightOperand + 1)
        # Number
        return (Num(tokens[idx]), idx + 1)

    parsedExpression, nextIdx = parse_expression(0)
    return parsedExpression

if __name__ == '__main__':
    doctest.testmod()
    print(tokenize('(x + 33)'))
