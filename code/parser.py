# parser.py

from errors import ErrorCollection, ParseError
from token import TokenType
from ast import *


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.errors = []

    # =========================
    # UTIL
    # =========================
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise ParseError(
                f"Unexpected token {self.current_token.type.name}, expected {token_type.name}",
                self.current_token.line,
                self.current_token.column,
            )

    def synchronize(self):
        while self.current_token.type not in (
            TokenType.SEMICOLON,
            TokenType.RBRACE,
            TokenType.EOF,
        ):
            self.current_token = self.lexer.get_next_token()

        if self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)

    # =========================
    # PROGRAM
    # =========================
    def parse(self):
        start = self.current_token
        self.eat(TokenType.BEGIN)
        block = self.block()
        self.eat(TokenType.END)
        if self.errors:
            raise ErrorCollection("Syntax analysis", self.errors)
        return Program(block, start.line, start.column)

    # =========================
    # BLOCK
    # =========================
    def block(self):
        start = self.current_token
        self.eat(TokenType.LBRACE)

        decls = []
        stmts = []

        # DECL LIST
        while self.current_token.type in (
            TokenType.INT, TokenType.BOOL, TokenType.FLOAT,
            TokenType.STRING, TokenType.AUTO
        ):
            try:
                decls.append(self.declaration())
            except ParseError as error:
                self.errors.append(error)
                self.synchronize()

        # STMT LIST
        while self.current_token.type not in (TokenType.RBRACE, TokenType.EOF):
            try:
                stmts.append(self.statement())
            except ParseError as error:
                self.errors.append(error)
                self.synchronize()

        self.eat(TokenType.RBRACE)
        return Block(decls, stmts, start.line, start.column)

    # =========================
    # DECL
    # =========================
    def declaration(self):
        start = self.current_token
        var_type = self.current_token.type.name.lower()
        self.eat(self.current_token.type)

        name_token = self.current_token
        name = name_token.value
        self.eat(TokenType.IDENTIFIER)

        expr = None
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            expr = self.expr()

        self.eat(TokenType.SEMICOLON)
        return VarDecl(var_type, name, expr, name_token.line, name_token.column)

    # =========================
    # STATEMENT
    # =========================
    def statement(self):
        token = self.current_token.type

        if token == TokenType.IDENTIFIER:
            return self.assign_stmt()

        elif token == TokenType.PRINT:
            return self.print_stmt()

        elif token == TokenType.INPUT:
            return self.input_stmt()

        elif token == TokenType.IF:
            return self.if_stmt()

        elif token == TokenType.FOR:
            return self.for_stmt()

        elif token == TokenType.DO:
            return self.while_stmt()

        elif token == TokenType.LBRACE:
            return self.block()

        else:
            raise ParseError(
                f"Invalid statement starting with {self.current_token.type.name}",
                self.current_token.line,
                self.current_token.column,
            )

    # =========================
    # ASSIGN
    # =========================
    def assign_stmt(self):
        name_token = self.current_token
        name = name_token.value
        self.eat(TokenType.IDENTIFIER)

        self.eat(TokenType.ASSIGN)
        expr = self.expr()

        self.eat(TokenType.SEMICOLON)
        return Assign(name, expr, name_token.line, name_token.column)

    # =========================
    # PRINT
    # =========================
    def print_stmt(self):
        start = self.current_token
        self.eat(TokenType.PRINT)

        self.eat(TokenType.LPAREN)
        expr = self.expr()
        self.eat(TokenType.RPAREN)

        self.eat(TokenType.SEMICOLON)
        return Print(expr, start.line, start.column)

    # =========================
    # INPUT
    # =========================
    def input_stmt(self):
        start = self.current_token
        self.eat(TokenType.INPUT)

        self.eat(TokenType.LPAREN)
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.RPAREN)

        self.eat(TokenType.SEMICOLON)
        return Input(name, start.line, start.column)

    # =========================
    # IF
    # =========================
    def if_stmt(self):
        start = self.current_token
        self.eat(TokenType.IF)

        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)

        self.eat(TokenType.THEN)
        then_branch = self.statement()

        # elseif list
        elif_branches = []
        while self.current_token.type == TokenType.ELSEIF:
            elif_start = self.current_token
            self.eat(TokenType.ELSEIF)

            self.eat(TokenType.LPAREN)
            cond = self.expr()
            self.eat(TokenType.RPAREN)

            stmt = self.statement()
            elif_branches.append(ElseIf(cond, stmt, elif_start.line, elif_start.column))

        # else
        else_branch = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            else_branch = self.statement()

        return If(condition, then_branch, elif_branches, else_branch, start.line, start.column)

    # =========================
    # FOR
    # =========================
    def for_stmt(self):
        start_token = self.current_token
        self.eat(TokenType.FOR)

        self.eat(TokenType.LPAREN)

        var = self.current_token.value
        self.eat(TokenType.IDENTIFIER)

        self.eat(TokenType.ASSIGN)
        start = self.expr()

        self.eat(TokenType.TO)
        end = self.expr()

        self.eat(TokenType.STEP)
        step = self.expr()

        self.eat(TokenType.RPAREN)

        body = self.statement()
        return For(var, start, end, step, body, start_token.line, start_token.column)

    # =========================
    # WHILE (do-while)
    # =========================
    def while_stmt(self):
        start = self.current_token
        self.eat(TokenType.DO)

        body = self.statement()

        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)

        condition = self.expr()

        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)

        return While(body, condition, start.line, start.column)

    # =========================
    # EXPRESSIONS
    # =========================
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
        while self.current_token.type in (
            TokenType.GT, TokenType.GE,
            TokenType.LT, TokenType.LE
        ):
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

        if self.current_token.type == TokenType.MINUS:
            op = self.current_token
            self.eat(TokenType.MINUS)
            return UnaryOp(op, self.unary())

        return self.primary()

    def primary(self):
        token = self.current_token

        if token.type == TokenType.INT_LITERAL:
            self.eat(TokenType.INT_LITERAL)
            return Num(token.value, token.line, token.column)

        if token.type == TokenType.FLOAT_LITERAL:
            self.eat(TokenType.FLOAT_LITERAL)
            return Num(token.value, token.line, token.column)

        if token.type == TokenType.STRING_LITERAL:
            self.eat(TokenType.STRING_LITERAL)
            return String(token.value, token.line, token.column)

        if token.type in (TokenType.TRUE, TokenType.FALSE):
            self.eat(token.type)
            return Bool(token.type == TokenType.TRUE, token.line, token.column)

        if token.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            return Var(token.value, token.line, token.column)

        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node

        raise ParseError(
            f"Invalid expression starting with {token.type.name}",
            token.line,
            token.column,
        )
