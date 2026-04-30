# Enum dùng để định nghĩa tất cả các loại token trong ngôn ngữ
from enum import Enum, auto


class TokenType(Enum):
    # 1. KEYWORDS (từ khóa)
    BEGIN = auto()
    END = auto()

    INT = auto()
    BOOL = auto()
    FLOAT = auto()
    STRING = auto()
    AUTO = auto()

    IF = auto()
    THEN = auto()
    ELSE = auto()
    ELSEIF = auto()

    DO = auto()
    WHILE = auto()

    FOR = auto()
    TO = auto()
    STEP = auto()

    PRINT = auto()
    INPUT = auto()

    TRUE = auto()
    FALSE = auto()

    # 2. IDENTIFIER & LITERALS
    IDENTIFIER = auto()      # tên biến
    INT_LITERAL = auto()     # số nguyên
    FLOAT_LITERAL = auto()   # số thực
    STRING_LITERAL = auto()  # chuỗi

    # 3. OPERATORS (toán tử)
    PLUS = auto()    # +
    MINUS = auto()   # -
    MUL = auto()     # *
    DIV = auto()     # /

    ASSIGN = auto()  # =
    
    EQ = auto()      # ==
    GT = auto()      # >
    GE = auto()      # >=
    LT = auto()      # <
    LE = auto()      # <=
    AND = auto()     # &&
    OR = auto()      # ||
    NOT = auto()     # !

    # 4. SEPARATORS (ký tự phân tách)
    SEMICOLON = auto()  # ;
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }

    # End of file
    EOF = auto()


class Token:
    """
    Class biểu diễn một token sau khi lexer phân tích.
    """

    def __init__(self, type_, value, line, column):
        self.type = type_      # loại token (TokenType)
        self.value = value     # giá trị thực tế (vd: "x", 10, "+")
        self.line = line       # dòng xuất hiện
        self.column = column   # cột xuất hiện

    def __repr__(self):
        # Hiển thị token khi print
        return f"{self.type.name}({self.value}) at {self.line}:{self.column}"