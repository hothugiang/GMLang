class AST:
    def set_location(self, line=None, column=None):
        self.line = line
        self.column = column
        return self


class Program(AST):
    def __init__(self, block, line=None, column=None):
        self.block = block
        self.set_location(line, column)


class Block(AST):
    def __init__(self, declarations, statements, line=None, column=None):
        self.declarations = declarations
        self.statements = statements
        self.set_location(line, column)


class VarDecl(AST):
    def __init__(self, var_type, name, expr=None, line=None, column=None):
        self.var_type = var_type
        self.name = name
        self.expr = expr
        self.set_location(line, column)


class Assign(AST):
    def __init__(self, name, expr, line=None, column=None):
        self.name = name
        self.expr = expr
        self.set_location(line, column)

class Input(AST):
    def __init__(self, name, line=None, column=None):
        self.name = name
        self.set_location(line, column)

class Print(AST):
    def __init__(self, expr, line=None, column=None):
        self.expr = expr
        self.set_location(line, column)

class If(AST):
    def __init__(self, condition, then_branch, elif_branches, else_branch, line=None, column=None):
        self.condition = condition
        self.then_branch = then_branch
        self.elif_branches = elif_branches  # list
        self.else_branch = else_branch
        self.set_location(line, column)

class ElseIf(AST):
    def __init__(self, condition, stmt, line=None, column=None):
        self.condition = condition
        self.stmt = stmt
        self.set_location(line, column)

class For(AST):
    def __init__(self, var, start, end, step, body, line=None, column=None):
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body
        self.set_location(line, column)


class BinOp(AST):
    def __init__(self, left, op, right, line=None, column=None):
        self.left = left
        self.op = op
        self.right = right
        self.set_location(line if line is not None else op.line, column if column is not None else op.column)


class UnaryOp(AST):
    def __init__(self, op, expr, line=None, column=None):
        self.op = op
        self.expr = expr
        self.set_location(line if line is not None else op.line, column if column is not None else op.column)


class Num(AST):
    def __init__(self, value, line=None, column=None):
        self.value = value
        self.type = type(value)
        self.set_location(line, column)


class String(AST):
    def __init__(self, value, line=None, column=None):
        self.value = value
        self.set_location(line, column)


class Bool(AST):
    def __init__(self, value, line=None, column=None):
        self.value = value
        self.set_location(line, column)

# class Float(AST):
#     def __init__(self, value):
#         self.value = value

class Var(AST):
    def __init__(self, name, line=None, column=None):
        self.name = name
        self.set_location(line, column)

class While(AST):
    def __init__(self,body, condition, line=None, column=None):
        self.body = body
        self.condition = condition
        self.set_location(line, column)
