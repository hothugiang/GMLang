class AST:
    pass


class Program(AST):
    def __init__(self, block):
        self.block = block


class Block(AST):
    def __init__(self, declarations, statements):
        self.declarations = declarations
        self.statements = statements


class VarDecl(AST):
    def __init__(self, var_type, name, expr=None):
        self.var_type = var_type
        self.name = name
        self.expr = expr


class Assign(AST):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr


class Print(AST):
    def __init__(self, expr):
        self.expr = expr


class If(AST):
    def __init__(self, condition, then_branch, elif_branches, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.elif_branches = elif_branches  # list
        self.else_branch = else_branch

class ElseIf(AST):
    def __init__(self, condition, stmt):
        self.condition = condition
        self.stmt = stmt

class For(AST):
    def __init__(self, var, start, end, step, body):
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr


class Num(AST):
    def __init__(self, value):
        self.value = value
        self.type = type(value)


class String(AST):
    def __init__(self, value):
        self.value = value


class Bool(AST):
    def __init__(self, value):
        self.value = value

class Float(AST):
    def __init__(self, value):
        self.value = value
        
class Var(AST):
    def __init__(self, name):
        self.name = name