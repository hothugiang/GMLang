# lexer.py

import re
from token import Token, TokenType


class Lexer:
    """
    Lexer (Lexical Analyzer):
    Nhiệm vụ: đọc source code và chia thành các token.
    """

    def __init__(self, text):
        self.text = text
        self.pos = 0         # vị trí hiện tại trong chuỗi
        self.line = 1        # dòng hiện tại
        self.col = 1         # cột hiện tại

    # Lấy ký tự hiện tại
    def current_char(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    # Di chuyển sang ký tự tiếp theo
    def advance(self):
        if self.current_char() == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1

    
    # Bỏ qua khoảng trắng (space, tab, newline)
    def skip_whitespace(self):
        while self.current_char() and self.current_char().isspace():
            self.advance()

    # Bỏ qua comment
    def skip_comment(self):
        # Comment 1 dòng: //
        if self.text[self.pos:self.pos+2] == "//":
            while self.current_char() and self.current_char() != '\n':
                self.advance()

        # Comment nhiều dòng: /* ... */
        elif self.text[self.pos:self.pos+2] == "/*":
            self.advance()
            self.advance()
            while self.current_char() and self.text[self.pos:self.pos+2] != "*/":
                self.advance()
            self.advance()
            self.advance()

    # Xử lý số (int hoặc float)
    def number(self):
        start_col = self.col
        num_str = ""

        # đọc phần nguyên
        while self.current_char() and self.current_char().isdigit():
            num_str += self.current_char()
            self.advance()

        # nếu có dấu . → float
        if self.current_char() == '.':
            num_str += '.'
            self.advance()

            while self.current_char() and self.current_char().isdigit():
                num_str += self.current_char()
                self.advance()

            return Token(TokenType.FLOAT_LITERAL, float(num_str), self.line, start_col)

        return Token(TokenType.INT_LITERAL, int(num_str), self.line, start_col)

    # Xử lý chuỗi "..."
    def string(self):
        start_col = self.col
        self.advance()  # bỏ dấu "

        result = ""

        while self.current_char() and self.current_char() != '"':
            result += self.current_char()
            self.advance()

        self.advance()  # bỏ dấu "

        return Token(TokenType.STRING_LITERAL, result, self.line, start_col)

    # Xử lý identifier hoặc keyword
    def identifier(self):
        start_col = self.col
        result = ""

        # đọc chữ + số
        while self.current_char() and self.current_char().isalnum():
            result += self.current_char()
            self.advance()

        # danh sách keyword
        keywords = {
            "begin": TokenType.BEGIN,
            "end": TokenType.END,
            "int": TokenType.INT,
            "bool": TokenType.BOOL,
            "float": TokenType.FLOAT,
            "string": TokenType.STRING,
            "auto": TokenType.AUTO,
            "if": TokenType.IF,
            "then": TokenType.THEN,
            "else": TokenType.ELSE,
            "elseif": TokenType.ELSEIF,
            "do": TokenType.DO,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "to": TokenType.TO,
            "step": TokenType.STEP,
            "print": TokenType.PRINT,
            "input": TokenType.INPUT,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
        }

        # nếu là keyword → trả keyword, không thì là identifier
        token_type = keywords.get(result, TokenType.IDENTIFIER)

        return Token(token_type, result, self.line, start_col)

    # Hàm chính: lấy token tiếp theo
    def get_next_token(self):
        while self.current_char():

            # bỏ whitespace
            if self.current_char().isspace():
                self.skip_whitespace()
                continue

            # bỏ comment
            if self.text[self.pos:self.pos+2] in ("//", "/*"):
                self.skip_comment()
                continue

            # số
            if self.current_char().isdigit():
                return self.number()

            # chuỗi
            if self.current_char() == '"':
                return self.string()

            # identifier / keyword
            if self.current_char().isalpha():
                return self.identifier()

            # Toán tử 2 ký tự
            if self.text[self.pos:self.pos+2] == "==":
                line, col = self.line, self.col
                self.advance(); self.advance()
                return Token(TokenType.EQ, "==", line, col)

            if self.text[self.pos:self.pos+2] == ">=":
                line, col = self.line, self.col
                self.advance(); self.advance()
                return Token(TokenType.EQ, ">=", line, col)
            
            if self.text[self.pos:self.pos+2] == "<=":
                line, col = self.line, self.col
                self.advance(); self.advance()
                return Token(TokenType.EQ, "<=", line, col)

            if self.text[self.pos:self.pos+2] == "&&":
                line, col = self.line, self.col
                self.advance(); self.advance()
                return Token(TokenType.EQ, "&&", line, col)

            if self.text[self.pos:self.pos+2] == "||":
                line, col = self.line, self.col
                self.advance(); self.advance()
                return Token(TokenType.EQ, "||", line, col)

            # Toán tử 1 ký tự
            char = self.current_char()

            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MUL,
                '/': TokenType.DIV,
                '=': TokenType.ASSIGN,
                '>': TokenType.GT,
                '<': TokenType.LT,
                '!': TokenType.NOT,
                ';': TokenType.SEMICOLON,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
            }

            if char in single_char_tokens:
                token_type = single_char_tokens[char]
                line, col = self.line, self.col
                self.advance()
                return Token(token_type, char, line, col)

            # nếu gặp ký tự lạ → lỗi
            raise Exception(f"Invalid character: {char} at {self.line}:{self.col}")

        # kết thúc file
        return Token(TokenType.EOF, None, self.line, self.col)