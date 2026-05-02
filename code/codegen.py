from ast import (
    Assign,
    BinOp,
    Block,
    Bool,
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
from errors import CodeGenError


class CodeGenerator:
    def __init__(self, class_name="Main"):
        self.class_name = class_name
        self.instructions = []
        self.scopes = []
        self.next_slot = 1
        self.label_count = 0
        self.scope_names = []
        self.scope_counter = 0
        self.symbol_table = []
        self.scanner_slot = None

    def generate(self, node):
        self.visit(node)
        return "\n".join(self.instructions)

    def emit(self, instruction=""):
        self.instructions.append(instruction)

    def new_label(self, prefix):
        label = f"{prefix}_{self.label_count}"
        self.label_count += 1
        return label

    def visit(self, node):
        method_name = "visit_" + type(node).__name__
        method = getattr(self, method_name, None)
        if method is None:
            raise CodeGenError(f"No code generation rule for {type(node).__name__}")
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

    def declare(self, name, var_type):
        current_scope = self.scopes[-1]
        slot = self.next_slot
        self.next_slot += 1
        current_scope[name] = {
            "name": name,
            "type": var_type,
            "scope": self.scope_names[-1],
            "index": slot,
            "slot": slot,
        }
        self.symbol_table.append(current_scope[name])
        return current_scope[name]

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise CodeGenError(f"Variable '{name}' is not declared")

    def infer_type(self, node):
        if isinstance(node, Num):
            if isinstance(node.value, int):
                return "int"
            if isinstance(node.value, float):
                return "float"

        if isinstance(node, Bool):
            return "bool"

        if isinstance(node, String):
            return "string"

        if isinstance(node, Var):
            return self.lookup(node.name)["type"]

        if isinstance(node, UnaryOp):
            operator = node.op.value
            expr_type = self.infer_type(node.expr)
            if operator == "!":
                return "bool"
            if operator == "-":
                return expr_type

        if isinstance(node, BinOp):
            operator = node.op.value
            left_type = self.infer_type(node.left)
            right_type = self.infer_type(node.right)

            if operator in ("+", "-", "*", "/"):
                if left_type == "float" or right_type == "float":
                    return "float"
                return "int"

            if operator in (">", ">=", "<", "<=", "==", "&&", "||"):
                return "bool"

        raise CodeGenError(f"Cannot infer type for {type(node).__name__}")

    def load_instruction(self, var_type, slot):
        if var_type in ("int", "bool"):
            return f"iload {slot}"
        if var_type == "float":
            return f"fload {slot}"
        if var_type == "string":
            return f"aload {slot}"
        raise CodeGenError(f"Unsupported load type '{var_type}'")

    def store_instruction(self, var_type, slot):
        if var_type in ("int", "bool"):
            return f"istore {slot}"
        if var_type == "float":
            return f"fstore {slot}"
        if var_type == "string":
            return f"astore {slot}"
        raise CodeGenError(f"Unsupported store type '{var_type}'")

    def println_descriptor(self, expr_type):
        if expr_type == "int":
            return "(I)V"
        if expr_type == "bool":
            return "(Z)V"
        if expr_type == "float":
            return "(F)V"
        if expr_type == "string":
            return "(Ljava/lang/String;)V"
        raise CodeGenError(f"Cannot print type '{expr_type}'")

    def emit_int_constant(self, value):
        if value == -1:
            self.emit("iconst_m1")
        elif 0 <= value <= 5:
            self.emit(f"iconst_{value}")
        elif -128 <= value <= 127:
            self.emit(f"bipush {value}")
        elif -32768 <= value <= 32767:
            self.emit(f"sipush {value}")
        else:
            self.emit(f"ldc {value}")

    def emit_default_value(self, var_type):
        if var_type in ("int", "bool"):
            self.emit("iconst_0")
        elif var_type == "float":
            self.emit("ldc 0.0")
        elif var_type == "string":
            self.emit('ldc ""')
        else:
            raise CodeGenError(f"Unsupported default type '{var_type}'")

    def emit_numeric_conversion(self, from_type, to_type):
        if from_type == "int" and to_type == "float":
            self.emit("i2f")

    def ensure_scanner(self):
        if self.scanner_slot is not None:
            return self.scanner_slot

        self.scanner_slot = self.next_slot
        self.next_slot += 1
        self.emit("new java/util/Scanner")
        self.emit("dup")
        self.emit("getstatic java/lang/System/in Ljava/io/InputStream;")
        self.emit("invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V")
        self.emit(f"astore {self.scanner_slot}")
        return self.scanner_slot

    def visit_Program(self, node: Program):
        self.emit(f".class public {self.class_name}")
        self.emit(".super java/lang/Object")
        self.emit()
        self.emit(".method public <init>()V")
        self.emit("aload_0")
        self.emit("invokespecial java/lang/Object/<init>()V")
        self.emit("return")
        self.emit(".end method")
        self.emit()
        self.emit(".method public static main([Ljava/lang/String;)V")
        self.emit(".limit stack 100")
        self.emit(".limit locals 100")
        self.emit()

        self.visit(node.block)

        self.emit("return")
        self.emit(".end method")

    def visit_Block(self, node: Block):
        self.enter_scope()

        for declaration in node.declarations:
            self.visit(declaration)

        for statement in node.statements:
            self.visit(statement)

        self.exit_scope()

    def visit_VarDecl(self, node: VarDecl):
        var_type = node.var_type
        if var_type == "auto":
            var_type = self.infer_type(node.expr)

        symbol = self.declare(node.name, var_type)

        if node.expr is None:
            self.emit_default_value(var_type)
        else:
            expr_type = self.visit(node.expr)
            self.emit_numeric_conversion(expr_type, var_type)

        self.emit(self.store_instruction(var_type, symbol["slot"]))

    def visit_Assign(self, node: Assign):
        symbol = self.lookup(node.name)
        expr_type = self.visit(node.expr)
        self.emit_numeric_conversion(expr_type, symbol["type"])
        self.emit(self.store_instruction(symbol["type"], symbol["slot"]))

    def visit_Input(self, node: Input):
        symbol = self.lookup(node.name)
        scanner_slot = self.ensure_scanner()
        methods = {
            "int": "nextInt()I",
            "bool": "nextBoolean()Z",
            "float": "nextFloat()F",
            "string": "next()Ljava/lang/String;",
        }

        if symbol["type"] not in methods:
            raise CodeGenError(f"Cannot input value for type '{symbol['type']}'")

        self.emit(f"aload {scanner_slot}")
        self.emit(f"invokevirtual java/util/Scanner/{methods[symbol['type']]}")
        self.emit(self.store_instruction(symbol["type"], symbol["slot"]))

    def visit_Print(self, node: Print):
        expr_type = self.infer_type(node.expr)
        self.emit("getstatic java/lang/System/out Ljava/io/PrintStream;")
        self.visit(node.expr)
        self.emit(f"invokevirtual java/io/PrintStream/println{self.println_descriptor(expr_type)}")

    def visit_If(self, node: If):
        end_label = self.new_label("if_end")
        next_label = self.new_label("if_next")

        self.visit(node.condition)
        self.emit(f"ifeq {next_label}")
        self.visit(node.then_branch)
        self.emit(f"goto {end_label}")
        self.emit(f"{next_label}:")

        for branch in node.elif_branches:
            next_label = self.new_label("if_next")
            self.visit(branch.condition)
            self.emit(f"ifeq {next_label}")
            self.visit(branch.stmt)
            self.emit(f"goto {end_label}")
            self.emit(f"{next_label}:")

        if node.else_branch is not None:
            self.visit(node.else_branch)

        self.emit(f"{end_label}:")

    def visit_For(self, node: For):
        symbol = self.lookup(node.var)
        start_label = self.new_label("for_start")
        positive_step_label = self.new_label("for_positive_step")
        negative_step_label = self.new_label("for_negative_step")
        body_label = self.new_label("for_body")
        end_label = self.new_label("for_end")

        self.visit(node.start)
        self.emit(self.store_instruction(symbol["type"], symbol["slot"]))

        self.emit(f"{start_label}:")
        self.visit(node.step)
        self.emit("iconst_0")
        self.emit(f"if_icmpgt {positive_step_label}")
        self.visit(node.step)
        self.emit("iconst_0")
        self.emit(f"if_icmplt {negative_step_label}")
        self.emit(f"goto {end_label}")

        self.emit(f"{positive_step_label}:")
        self.emit(self.load_instruction(symbol["type"], symbol["slot"]))
        self.visit(node.end)
        self.emit(f"if_icmpgt {end_label}")
        self.emit(f"goto {body_label}")

        self.emit(f"{negative_step_label}:")
        self.emit(self.load_instruction(symbol["type"], symbol["slot"]))
        self.visit(node.end)
        self.emit(f"if_icmplt {end_label}")

        self.emit(f"{body_label}:")
        self.visit(node.body)

        self.emit(self.load_instruction(symbol["type"], symbol["slot"]))
        self.visit(node.step)
        self.emit("iadd")
        self.emit(self.store_instruction(symbol["type"], symbol["slot"]))
        self.emit(f"goto {start_label}")
        self.emit(f"{end_label}:")

    def visit_While(self, node: While):
        start_label = self.new_label("do_start")

        self.emit(f"{start_label}:")
        self.visit(node.body)
        self.visit(node.condition)
        self.emit(f"ifne {start_label}")

    def visit_BinOp(self, node: BinOp):
        operator = node.op.value
        left_type = self.infer_type(node.left)
        right_type = self.infer_type(node.right)
        result_type = self.infer_type(node)

        if operator in ("+", "-", "*", "/"):
            self.visit(node.left)
            self.emit_numeric_conversion(left_type, result_type)
            self.visit(node.right)
            self.emit_numeric_conversion(right_type, result_type)

            if result_type == "int":
                instructions = {"+": "iadd", "-": "isub", "*": "imul", "/": "idiv"}
            else:
                instructions = {"+": "fadd", "-": "fsub", "*": "fmul", "/": "fdiv"}

            self.emit(instructions[operator])
            return result_type

        if operator in (">", ">=", "<", "<=", "=="):
            self.emit_comparison(node, left_type, right_type, operator)
            return "bool"

        if operator == "&&":
            self.visit(node.left)
            self.visit(node.right)
            self.emit("iand")
            return "bool"

        if operator == "||":
            self.visit(node.left)
            self.visit(node.right)
            self.emit("ior")
            return "bool"

        raise CodeGenError(f"Unknown binary operator '{operator}'")

    def emit_comparison(self, node, left_type, right_type, operator):
        if operator == "==" and left_type == "string" and right_type == "string":
            self.visit(node.left)
            self.visit(node.right)
            self.emit("invokevirtual java/lang/String/equals(Ljava/lang/Object;)Z")
            return

        true_label = self.new_label("cmp_true")
        end_label = self.new_label("cmp_end")

        result_type = "float" if left_type == "float" or right_type == "float" else left_type
        self.visit(node.left)
        self.emit_numeric_conversion(left_type, result_type)
        self.visit(node.right)
        self.emit_numeric_conversion(right_type, result_type)

        if result_type == "float":
            self.emit("fcmpl")
            jumps = {
                ">": "ifgt",
                ">=": "ifge",
                "<": "iflt",
                "<=": "ifle",
                "==": "ifeq",
            }
        else:
            jumps = {
                ">": "if_icmpgt",
                ">=": "if_icmpge",
                "<": "if_icmplt",
                "<=": "if_icmple",
                "==": "if_icmpeq",
            }

        self.emit(f"{jumps[operator]} {true_label}")
        self.emit("iconst_0")
        self.emit(f"goto {end_label}")
        self.emit(f"{true_label}:")
        self.emit("iconst_1")
        self.emit(f"{end_label}:")

    def visit_UnaryOp(self, node: UnaryOp):
        operator = node.op.value
        expr_type = self.visit(node.expr)

        if operator == "-":
            if expr_type == "int":
                self.emit("ineg")
            elif expr_type == "float":
                self.emit("fneg")
            else:
                raise CodeGenError("Unary '-' only supports int and float")
            return expr_type

        if operator == "!":
            true_label = self.new_label("not_true")
            end_label = self.new_label("not_end")
            self.emit(f"ifeq {true_label}")
            self.emit("iconst_0")
            self.emit(f"goto {end_label}")
            self.emit(f"{true_label}:")
            self.emit("iconst_1")
            self.emit(f"{end_label}:")
            return "bool"

        raise CodeGenError(f"Unknown unary operator '{operator}'")

    def visit_Num(self, node: Num):
        if isinstance(node.value, int):
            self.emit_int_constant(node.value)
            return "int"

        if isinstance(node.value, float):
            self.emit(f"ldc {node.value}")
            return "float"

        raise CodeGenError(f"Unsupported number literal: {node.value}")

    def visit_String(self, node: String):
        escaped = node.value.replace("\\", "\\\\").replace('"', '\\"')
        self.emit(f'ldc "{escaped}"')
        return "string"

    def visit_Bool(self, node: Bool):
        self.emit("iconst_1" if node.value else "iconst_0")
        return "bool"

    def visit_Var(self, node: Var):
        symbol = self.lookup(node.name)
        self.emit(self.load_instruction(symbol["type"], symbol["slot"]))
        return symbol["type"]
