import subprocess
import sys
import unittest
import importlib.util
import importlib
import shutil
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
sys.path.insert(0, str(CODE_DIR))

# Repo có ast.py/token.py trùng tên module chuẩn, nên cần nạp local tạm thời.
stdlib_ast = importlib.import_module("ast")
stdlib_token = importlib.import_module("token")


def load_local_module(module_name):
    """Nạp module local trong thư mục code/."""
    spec = importlib.util.spec_from_file_location(module_name, CODE_DIR / f"{module_name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


local_ast = load_local_module("ast")
local_token = load_local_module("token")

try:
    classfile_module = importlib.import_module("classfile")
    codegen_module = importlib.import_module("codegen")
    errors_module = importlib.import_module("errors")
    lexer_module = importlib.import_module("lexer")
    parser_module = importlib.import_module("parser")
    semantic_module = importlib.import_module("semantic")
finally:
    # Khôi phục module chuẩn để unittest/traceback không lỗi.
    sys.modules["ast"] = stdlib_ast
    sys.modules["token"] = stdlib_token


assemble_class = classfile_module.assemble_class
CodeGenerator = codegen_module.CodeGenerator
ErrorCollection = errors_module.ErrorCollection
LexicalError = errors_module.LexicalError
Lexer = lexer_module.Lexer
Parser = parser_module.Parser
SemanticAnalyzer = semantic_module.SemanticAnalyzer
TokenType = local_token.TokenType


def parse_source(source):
    """Chạy lexer + parser và trả về AST."""
    return Parser(Lexer(source)).parse()


def analyze_source(source):
    """Chạy đến semantic analyzer."""
    ast = parse_source(source)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return ast, analyzer


def compile_to_assembly(source, class_name="Main"):
    """Sinh JVM instruction text, chưa ghi file."""
    ast, _ = analyze_source(source)
    return CodeGenerator(class_name).generate(ast)


def compile_and_run(source, stdin_text=""):
    """Compile ra .class tạm và chạy bằng JVM."""
    temp_root = ROOT / "test_builds"
    temp_root.mkdir(exist_ok=True)

    output_dir = temp_root / f"case_{uuid.uuid4().hex}"
    output_dir.mkdir()

    try:
        class_name = "Main"
        assembly = compile_to_assembly(source, class_name)
        # Main.j để debug, Main.class để JVM chạy.
        (output_dir / f"{class_name}.j").write_text(assembly, encoding="utf-8")
        (output_dir / f"{class_name}.class").write_bytes(assemble_class(assembly))

        result = subprocess.run(
            ["java", "-cp", str(output_dir), class_name],
            input=stdin_text,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


class LexerTests(unittest.TestCase):
    """Test riêng phần lexer."""

    def collect_types(self, source):
        lexer = Lexer(source)
        types = []
        while True:
            token = lexer.get_next_token()
            types.append(token.type)
            if token.type == TokenType.EOF:
                return types

    def test_tokenizes_declaration(self):
        types = self.collect_types("int x = 10;")
        self.assertEqual(
            types,
            [
                TokenType.INT,
                TokenType.IDENTIFIER,
                TokenType.ASSIGN,
                TokenType.INT_LITERAL,
                TokenType.SEMICOLON,
                TokenType.EOF,
            ],
        )

    def test_rejects_digit_in_middle_of_identifier(self):
        with self.assertRaises(LexicalError):
            self.collect_types("int ab1c;")


class ParserAndSemanticTests(unittest.TestCase):
    """Test parser recovery và semantic."""

    def test_parser_recovers_multiple_syntax_errors(self):
        source = "begin { int x = ; bool y = true; print(y) print(x); } end"
        with self.assertRaises(ErrorCollection) as context:
            parse_source(source)
        self.assertGreaterEqual(len(context.exception.errors), 2)

    def test_auto_type_inference_records_symbol_type(self):
        _, analyzer = analyze_source("begin { auto x = 1; auto y = 2.5; } end")
        symbols = {symbol["name"]: symbol for symbol in analyzer.get_symbol_table()}
        self.assertEqual(symbols["x"]["type"], "int")
        self.assertEqual(symbols["y"]["type"], "float")

    def test_rejects_assignment_type_mismatch(self):
        with self.assertRaises(ErrorCollection):
            analyze_source("begin { int x; x = true; } end")

    def test_rejects_undeclared_variable(self):
        with self.assertRaises(ErrorCollection):
            analyze_source("begin { x = 1; } end")

    def test_rejects_zero_for_step(self):
        with self.assertRaises(ErrorCollection):
            analyze_source("begin { int x; for (x = 0 to 3 step 0) { print(x); } } end")

    def test_semantic_reports_multiple_errors(self):
        source = "begin { int x; x = true; y = 10; print(z); } end"
        with self.assertRaises(ErrorCollection) as context:
            analyze_source(source)
        self.assertGreaterEqual(len(context.exception.errors), 3)


class CodegenAndJvmTests(unittest.TestCase):
    """Test end-to-end: compile .class rồi chạy java."""

    def test_arithmetic_prints_result(self):
        output = compile_and_run("begin { int x = 1 + 2; print(x); } end")
        self.assertEqual(output.strip(), "3")

    def test_for_positive_step(self):
        output = compile_and_run(
            "begin { int x; for (x = 0 to 3 step 1) { print(x); } } end"
        )
        self.assertEqual(output.strip().splitlines(), ["0", "1", "2", "3"])

    def test_for_negative_step(self):
        output = compile_and_run(
            "begin { int x; for (x = 3 to 0 step -1) { print(x); } } end"
        )
        self.assertEqual(output.strip().splitlines(), ["3", "2", "1", "0"])

    def test_string_equality_compares_content(self):
        source = """
        begin {
            string a;
            string b;
            input(a);
            input(b);
            print(a == b);
        }
        end
        """
        self.assertEqual(compile_and_run(source, "hello\nhello\n").strip(), "true")
        self.assertEqual(compile_and_run(source, "hello\nworld\n").strip(), "false")

    def test_string_equality_uses_equals_call(self):
        assembly = compile_to_assembly(
            'begin { string a = "hi"; string b = "hi"; print(a == b); } end'
        )
        self.assertIn("java/lang/String/equals", assembly)

    def test_input_int(self):
        source = "begin { int x; input(x); print(x + 1); } end"
        self.assertEqual(compile_and_run(source, "41\n").strip(), "42")


if __name__ == "__main__":
    unittest.main()
