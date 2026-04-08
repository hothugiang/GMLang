# parser.py

from token import TokenType
from ast import *


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Lỗi cú pháp: Mong đợi {token_type} nhưng nhận được {self.current_token.type}")

    # ===== PROGRAM =====
    def parse(self):
        self.eat(TokenType.BEGIN)
        block = self.block()
        self.eat(TokenType.END)
        return Program(block)

    # ===== BLOCK =====
    def block(self):
        self.eat(TokenType.LBRACE)
        decls = []
        stmts = []

        while self.current_token.type in (
            TokenType.INT, TokenType.BOOL, TokenType.FLOAT,
            TokenType.STRING, TokenType.AUTO
        ):
            decls.append(self.declaration())

        while self.current_token.type not in (TokenType.RBRACE, TokenType.EOF):
            stmts.append(self.statement())

        self.eat(TokenType.RBRACE)
        return Block(decls, stmts)

    # ===== DECL =====
    def declaration(self):
        var_type_token = self.current_token.type
        var_type = var_type_token.name.lower()

        self.eat(var_type_token)

        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)

        expr = None
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            expr = self.expr()

        self.eat(TokenType.SEMICOLON)

        return VarDecl(var_type, name, expr)
    # ===== STATEMENT =====
    def statement(self):
        token = self.current_token.type

        if token == TokenType.IDENTIFIER:
            return self.assign_stmt()
        elif token == TokenType.PRINT:
            return self.print_stmt()
        elif token == TokenType.IF:
            return self.if_stmt()
        elif token == TokenType.FOR:
            return self.for_stmt()
        elif token == TokenType.LBRACE:
            return self.block()
        else:
            raise Exception(f"Invalid statement: {self.current_token}")

    # ===== ASSIGN =====
    def assign_stmt(self):
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        expr = self.expr()
        self.eat(TokenType.SEMICOLON)
        return Assign(name, expr)

    # ===== PRINT =====
    def print_stmt(self):
        self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        expr = self.expr()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)
        return Print(expr)

    # ===== IF =====
    def if_stmt(self):
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.THEN)

        then_branch = self.statement()

        # danh sách elseif
        elif_branches = []

        while self.current_token.type == TokenType.ELSEIF:
            self.eat(TokenType.ELSEIF)
            self.eat(TokenType.LPAREN)
            cond = self.expr()
            self.eat(TokenType.RPAREN)

            stmt = self.statement()
            elif_branches.append(ElseIf(cond, stmt))

        # else
        else_branch = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            else_branch = self.statement()

        return If(condition, then_branch, elif_branches, else_branch)

    # ===== FOR =====
    def for_stmt(self):
        self.eat(TokenType.FOR)

        var = self.current_token.value
        self.eat(TokenType.IDENTIFIER)

        self.eat(TokenType.ASSIGN)
        start = self.expr()

        self.eat(TokenType.TO)
        end = self.expr()

        step = None
        if self.current_token.type == TokenType.STEP:
            self.eat(TokenType.STEP)
            step = self.expr()

        body = self.block()
        return For(var, start, end, step, body)

    # ===== EXPRESSIONS =====
    def expr(self):
        node = self.and_expr()
        while self.current_token.type == TokenType.OR:
            op = self.current_token
            self.eat(TokenType.OR)
            node = BinOp(node, op, self.and_expr())
        return node

    def and_expr(self):
        node = self.equality()
        while self.current_token.type == TokenType.AND:
            op = self.current_token
            self.eat(TokenType.AND)
            node = BinOp(node, op, self.equality())
        return node

    def equality(self):
        node = self.relational()
        while self.current_token.type == TokenType.EQ:
            op = self.current_token
            self.eat(TokenType.EQ)
            node = BinOp(node, op, self.relational())
        return node

    def relational(self):
        node = self.add()
        while self.current_token.type in (TokenType.GT, TokenType.GE, TokenType.LT, TokenType.LE):
            op = self.current_token
            self.eat(op.type)
            node = BinOp(node, op, self.add())
        return node

    def add(self):
        node = self.mul()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token
            self.eat(op.type)
            node = BinOp(node, op, self.mul())
        return node

    def mul(self):
        node = self.unary()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            op = self.current_token
            self.eat(op.type)
            node = BinOp(node, op, self.unary())
        return node

    def unary(self):
        if self.current_token.type == TokenType.NOT:
            op = self.current_token
            self.eat(TokenType.NOT)
            return UnaryOp(op, self.unary())
        return self.primary()

    def primary(self):
        token = self.current_token

        if token.type == TokenType.INT_LITERAL:
            self.eat(TokenType.INT_LITERAL)
            return Num(token.value)

        if token.type == TokenType.FLOAT_LITERAL:
            self.eat(TokenType.FLOAT_LITERAL)
            return Num(token.value)

        if token.type == TokenType.STRING_LITERAL:
            self.eat(TokenType.STRING_LITERAL)
            return String(token.value)

        if token.type in (TokenType.TRUE, TokenType.FALSE):
            self.eat(token.type)
            return Bool(token.value)

        if token.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            return Var(token.value)

        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node

        raise Exception(f"Invalid expression: {token}")
    