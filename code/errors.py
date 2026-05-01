class CompileError(Exception):
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.__str__())

    def __str__(self):
        if self.line is not None and self.column is not None:
            return f"{self.message} at {self.line}:{self.column}"
        return self.message


class LexicalError(CompileError):
    pass


class ParseError(CompileError):
    pass


class SemanticError(CompileError):
    pass


class CodeGenError(CompileError):
    pass


class ErrorCollection(Exception):
    def __init__(self, phase, errors):
        self.phase = phase
        self.errors = errors
        message = "\n".join(str(error) for error in errors)
        super().__init__(f"{phase} failed with {len(errors)} error(s):\n{message}")
