import argparse
import subprocess
import sys
from pathlib import Path

from classfile import assemble_class
from codegen import CodeGenerator
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer


def compile_source(source, class_name="Main"):
    lexer = Lexer(source)
    parser = Parser(lexer)
    ast = parser.parse()

    semantic = SemanticAnalyzer()
    semantic.analyze(ast)

    generator = CodeGenerator(class_name)
    return generator.generate(ast)


def run_class(output_dir, class_name):
    result = subprocess.run(
        ["java", "-cp", str(output_dir), class_name],
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "JVM execution failed\n"
            + result.stdout
            + result.stderr
        )

    return result.stdout


def main():
    arg_parser = argparse.ArgumentParser(description="Compile GMLang source to JVM bytecode.")
    arg_parser.add_argument("source", help="Path to a GMLang source file")
    arg_parser.add_argument("--class-name", default="Main", help="Generated JVM class name")
    arg_parser.add_argument("--out-dir", default="build", help="Directory for generated files")
    arg_parser.add_argument("--run", action="store_true", help="Assemble and run on the JVM")
    args = arg_parser.parse_args()

    source_path = Path(args.source)
    output_dir = Path(args.out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source = source_path.read_text(encoding="utf-8")
    jvm_assembly = compile_source(source, args.class_name)

    assembly_file = output_dir / f"{args.class_name}.j"
    assembly_file.write_text(jvm_assembly, encoding="utf-8")
    print(f"Wrote {assembly_file}")

    class_file = output_dir / f"{args.class_name}.class"
    class_file.write_bytes(assemble_class(jvm_assembly))
    print(f"Wrote {class_file}")

    if not args.run:
        return

    output = run_class(output_dir, args.class_name)
    if output:
        print(output, end="")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
