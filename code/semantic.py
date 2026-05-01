from ast import (
    Assign,
    BinOp,
    Block,
    Bool,
    ElseIf,
    For,
    If,
    Input,
    Num,
    Print,
    Program,
    String,
    UnaryOp,
    Var,
    VarDecl,
    While,
)
from errors import SemanticError


class SemanticAnalyzer:
    def __init__(self):
        self.scopes = []
        self.scope_names = []
        self.scope_counter = 0
        self.next_index = 1
        self.symbol_table = []

    def analyze(self, node):
        self.scopes = []
        self.scope_names = []
        self.scope_counter = 0
        self.next_index = 1
        self.symbol_table = []
        self.visit(node)

    def visit(self, node):
        method_name = "visit_" + type(node).__name__
        method = getattr(self, method_name, None)
        if method is None:
            raise SemanticError(f"No semantic rule for {type(node).__name__}")
        return method(node)

    def enter_scope(self):
        if not self.scope_names:
            scope_name = "global"
        else:
            self.scope_counter += 1
            scope_name = f"block{self.scope_counter}"
        self.scopes.append({})
        self.scope_names.append(scope_name)

    def exit_scope(self):
        self.scopes.pop()
        self.scope_names.pop()

    def error(self, message, node=None):
        raise SemanticError(message, getattr(node, "line", None), getattr(node, "column", None))

    def declare(self, name, var_type, node=None):
        current_scope = self.scopes[-1]
        if name in current_scope:
            self.error(f"Variable '{name}' is already declared in this scope", node)

        symbol = {
            "name": name,
            "type": var_type,
            "scope": self.scope_names[-1],
            "index": self.next_index,
            "line": getattr(node, "line", None),
            "column": getattr(node, "column", None),
        }
        self.next_index += 1
        current_scope[name] = symbol
        self.symbol_table.append(symbol)
        return symbol

    def lookup(self, name, node=None):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        self.error(f"Variable '{name}' is not declared", node)

    def check_assignable(self, target_type, value_type, node=None):
        if target_type == value_type:
            return

        if target_type == "float" and value_type == "int":
            return

        self.error(f"Cannot assign {value_type} to {target_type}", node)

    def get_symbol_table(self):
        return list(self.symbol_table)

    def is_numeric(self, type_name):
        return type_name in ("int", "float")

    def visit_Program(self, node: Program):
        self.visit(node.block)

    def visit_Block(self, node: Block):
        self.enter_scope()

        for declaration in node.declarations:
            self.visit(declaration)

        for statement in node.statements:
            self.visit(statement)

        self.exit_scope()

    def visit_VarDecl(self, node: VarDecl):
        if node.var_type == "auto":
            if node.expr is None:
                self.error(f"Variable '{node.name}' declared with auto must have initializer", node)

            inferred_type = self.visit(node.expr)
            self.declare(node.name, inferred_type, node)
            return

        self.declare(node.name, node.var_type, node)

        if node.expr is not None:
            expr_type = self.visit(node.expr)
            self.check_assignable(node.var_type, expr_type, node.expr)

    def visit_Assign(self, node: Assign):
        symbol = self.lookup(node.name, node)
        expr_type = self.visit(node.expr)
        self.check_assignable(symbol["type"], expr_type, node.expr)

    def visit_Input(self, node: Input):
        self.lookup(node.name, node)

    def visit_Print(self, node: Print):
        self.visit(node.expr)

    def visit_If(self, node: If):
        condition_type = self.visit(node.condition)
        if condition_type != "bool":
            self.error("if condition must be bool", node.condition)

        self.visit(node.then_branch)

        for branch in node.elif_branches:
            self.visit(branch)

        if node.else_branch is not None:
            self.visit(node.else_branch)

    def visit_ElseIf(self, node: ElseIf):
        condition_type = self.visit(node.condition)
        if condition_type != "bool":
            self.error("elseif condition must be bool", node.condition)

        self.visit(node.stmt)

    def visit_For(self, node: For):
        symbol = self.lookup(node.var, node)
        if symbol["type"] != "int":
            self.error("for variable must be int", node)

        start_type = self.visit(node.start)
        end_type = self.visit(node.end)
        step_type = self.visit(node.step)

        if start_type != "int" or end_type != "int" or step_type != "int":
            self.error("for start, end and step expressions must be int", node)

        self.visit(node.body)

    def visit_While(self, node: While):
        self.visit(node.body)

        condition_type = self.visit(node.condition)
        if condition_type != "bool":
            self.error("while condition must be bool", node.condition)

    def visit_BinOp(self, node: BinOp):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        operator = node.op.value

        if operator in ("+", "-", "*", "/"):
            if not self.is_numeric(left_type) or not self.is_numeric(right_type):
                self.error(f"Operator '{operator}' requires numeric operands", node)

            if left_type == "float" or right_type == "float":
                return "float"
            return "int"

        if operator in (">", ">=", "<", "<="):
            if not self.is_numeric(left_type) or not self.is_numeric(right_type):
                self.error(f"Operator '{operator}' requires numeric operands", node)
            return "bool"

        if operator == "==":
            if left_type == right_type or (self.is_numeric(left_type) and self.is_numeric(right_type)):
                return "bool"
            self.error("Operator '==' requires operands of compatible types", node)

        if operator in ("&&", "||"):
            if left_type != "bool" or right_type != "bool":
                self.error(f"Operator '{operator}' requires bool operands", node)
            return "bool"

        self.error(f"Unknown binary operator '{operator}'", node)

    def visit_UnaryOp(self, node: UnaryOp):
        expr_type = self.visit(node.expr)
        operator = node.op.value

        if operator == "!":
            if expr_type != "bool":
                self.error("Operator '!' requires bool operand", node)
            return "bool"

        if operator == "-":
            if not self.is_numeric(expr_type):
                self.error("Unary '-' requires numeric operand", node)
            return expr_type

        self.error(f"Unknown unary operator '{operator}'", node)

    def visit_Num(self, node: Num):
        if isinstance(node.value, int):
            return "int"
        if isinstance(node.value, float):
            return "float"
        self.error(f"Unsupported number literal: {node.value}", node)

    def visit_String(self, node: String):
        return "string"

    def visit_Bool(self, node: Bool):
        return "bool"

    def visit_Var(self, node: Var):
        return self.lookup(node.name, node)["type"]
