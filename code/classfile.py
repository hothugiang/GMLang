import re
import struct


class ClassFileError(Exception):
    pass


class ConstantPool:
    def __init__(self):
        self.items = [None]
        self.cache = {}

    def add(self, key, item):
        if key in self.cache:
            return self.cache[key]
        self.items.append(item)
        index = len(self.items) - 1
        self.cache[key] = index
        return index

    def utf8(self, value):
        return self.add(("utf8", value), (1, value))

    def integer(self, value):
        return self.add(("int", value), (3, value))

    def float(self, value):
        return self.add(("float", value), (4, value))

    def class_ref(self, name):
        name_index = self.utf8(name)
        return self.add(("class", name), (7, name_index))

    def string(self, value):
        utf8_index = self.utf8(value)
        return self.add(("string", value), (8, utf8_index))

    def name_and_type(self, name, descriptor):
        name_index = self.utf8(name)
        descriptor_index = self.utf8(descriptor)
        return self.add(("nat", name, descriptor), (12, name_index, descriptor_index))

    def field_ref(self, class_name, name, descriptor):
        class_index = self.class_ref(class_name)
        nat_index = self.name_and_type(name, descriptor)
        return self.add(("field", class_name, name, descriptor), (9, class_index, nat_index))

    def method_ref(self, class_name, name, descriptor):
        class_index = self.class_ref(class_name)
        nat_index = self.name_and_type(name, descriptor)
        return self.add(("method", class_name, name, descriptor), (10, class_index, nat_index))

    def to_bytes(self):
        output = [u2(len(self.items))]
        for item in self.items[1:]:
            tag = item[0]
            output.append(u1(tag))

            if tag == 1:
                encoded = item[1].encode("utf-8")
                output.append(u2(len(encoded)))
                output.append(encoded)
            elif tag == 3:
                output.append(struct.pack(">i", item[1]))
            elif tag == 4:
                output.append(struct.pack(">f", item[1]))
            elif tag in (7, 8):
                output.append(u2(item[1]))
            elif tag in (9, 10, 12):
                output.append(u2(item[1]))
                output.append(u2(item[2]))
            else:
                raise ClassFileError(f"Unsupported constant pool tag {tag}")

        return b"".join(output)


def u1(value):
    return struct.pack(">B", value)


def u2(value):
    return struct.pack(">H", value)


def u4(value):
    return struct.pack(">I", value)


def s2(value):
    return struct.pack(">h", value)


def parse_assembly(jvm_assembly):
    class_name = None
    methods = []
    current_method = None

    for raw_line in jvm_assembly.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith(".class"):
            class_name = line.split()[-1]
            continue

        if line.startswith(".method"):
            parts = line.split()
            descriptor = parts[-1]
            name = parts[-1].split("(")[0]
            if "/" in name:
                name = name.split("/")[-1]
            if parts[-1].startswith("<init>"):
                name = "<init>"
                descriptor = "()V"
            elif current_method is None and "(" in descriptor:
                name = descriptor.split("(")[0]
                descriptor = descriptor[len(name):]

            current_method = {
                "name": name,
                "descriptor": descriptor,
                "access": 0x0009 if "static" in parts else 0x0001,
                "max_stack": 100,
                "max_locals": 100,
                "lines": [],
            }
            continue

        if line == ".end method":
            methods.append(current_method)
            current_method = None
            continue

        if current_method is not None:
            if line.startswith(".limit stack"):
                current_method["max_stack"] = int(line.split()[-1])
            elif line.startswith(".limit locals"):
                current_method["max_locals"] = int(line.split()[-1])
            elif not line.startswith("."):
                current_method["lines"].append(line)

    if class_name is None:
        raise ClassFileError("Missing .class directive")

    return class_name, methods


def instruction_size(line):
    if line.endswith(":"):
        return 0

    op = line.split()[0]

    if op in {
        "aload_0",
        "dup",
        "return",
        "iconst_m1",
        "iconst_0",
        "iconst_1",
        "iconst_2",
        "iconst_3",
        "iconst_4",
        "iconst_5",
        "iadd",
        "isub",
        "imul",
        "idiv",
        "ineg",
        "fadd",
        "fsub",
        "fmul",
        "fdiv",
        "fneg",
        "i2f",
        "fcmpl",
        "iand",
        "ior",
    }:
        return 1

    if op in {"bipush", "iload", "fload", "aload", "istore", "fstore", "astore", "ldc"}:
        return 2

    if op in {"sipush", "new"}:
        return 3

    if op in {
        "ifeq",
        "ifne",
        "iflt",
        "ifge",
        "ifgt",
        "ifle",
        "if_icmpeq",
        "if_icmpge",
        "if_icmpgt",
        "if_icmplt",
        "if_icmple",
        "if_acmpeq",
        "goto",
        "getstatic",
        "invokevirtual",
        "invokespecial",
    }:
        return 3

    raise ClassFileError(f"Unsupported instruction: {line}")


def collect_labels(lines):
    labels = {}
    pc = 0

    for line in lines:
        if line.endswith(":"):
            labels[line[:-1]] = pc
        else:
            pc += instruction_size(line)

    return labels


def parse_ldc_value(value):
    if value.startswith('"') and value.endswith('"'):
        return "string", bytes(value[1:-1], "utf-8").decode("unicode_escape")

    if "." in value:
        return "float", float(value)

    return "int", int(value)


def assemble_instruction(line, pc, labels, pool):
    no_arg_opcodes = {
        "aload_0": 0x2A,
        "dup": 0x59,
        "return": 0xB1,
        "iconst_m1": 0x02,
        "iconst_0": 0x03,
        "iconst_1": 0x04,
        "iconst_2": 0x05,
        "iconst_3": 0x06,
        "iconst_4": 0x07,
        "iconst_5": 0x08,
        "iadd": 0x60,
        "isub": 0x64,
        "imul": 0x68,
        "idiv": 0x6C,
        "ineg": 0x74,
        "fadd": 0x62,
        "fsub": 0x66,
        "fmul": 0x6A,
        "fdiv": 0x6E,
        "fneg": 0x76,
        "i2f": 0x86,
        "fcmpl": 0x95,
        "iand": 0x7E,
        "ior": 0x80,
    }

    branch_opcodes = {
        "ifeq": 0x99,
        "ifne": 0x9A,
        "iflt": 0x9B,
        "ifge": 0x9C,
        "ifgt": 0x9D,
        "ifle": 0x9E,
        "if_icmpeq": 0x9F,
        "if_icmpge": 0xA2,
        "if_icmpgt": 0xA3,
        "if_icmplt": 0xA1,
        "if_icmple": 0xA4,
        "if_acmpeq": 0xA5,
        "goto": 0xA7,
    }

    parts = line.split(maxsplit=1)
    op = parts[0]
    arg = parts[1] if len(parts) > 1 else None

    if op in no_arg_opcodes:
        return u1(no_arg_opcodes[op])

    if op == "bipush":
        return u1(0x10) + struct.pack(">b", int(arg))

    if op == "sipush":
        return u1(0x11) + s2(int(arg))

    if op == "new":
        index = pool.class_ref(arg)
        return u1(0xBB) + u2(index)

    if op in {"iload", "fload", "aload", "istore", "fstore", "astore"}:
        opcodes = {
            "iload": 0x15,
            "fload": 0x17,
            "aload": 0x19,
            "istore": 0x36,
            "fstore": 0x38,
            "astore": 0x3A,
        }
        return u1(opcodes[op]) + u1(int(arg))

    if op == "ldc":
        constant_type, value = parse_ldc_value(arg)
        if constant_type == "string":
            index = pool.string(value)
        elif constant_type == "float":
            index = pool.float(value)
        else:
            index = pool.integer(value)
        if index > 255:
            raise ClassFileError("ldc constant pool index is too large for this minimal assembler")
        return u1(0x12) + u1(index)

    if op in branch_opcodes:
        offset = labels[arg] - pc
        return u1(branch_opcodes[op]) + s2(offset)

    if op == "getstatic":
        class_name, field_name, descriptor = parse_member_ref(arg)
        index = pool.field_ref(class_name, field_name, descriptor)
        return u1(0xB2) + u2(index)

    if op in {"invokevirtual", "invokespecial"}:
        class_name, method_name, descriptor = parse_member_ref(arg)
        index = pool.method_ref(class_name, method_name, descriptor)
        opcode = 0xB6 if op == "invokevirtual" else 0xB7
        return u1(opcode) + u2(index)

    raise ClassFileError(f"Unsupported instruction: {line}")


def parse_member_ref(value):
    match = re.match(r"(.+)/([^/\s]+)\s+(.+)$", value)
    if match:
        return match.group(1), match.group(2), match.group(3)

    match = re.match(r"(.+)/([^/\s]+)(\(.*\).*)$", value)
    if match:
        return match.group(1), match.group(2), match.group(3)

    raise ClassFileError(f"Invalid member reference: {value}")


def assemble_method_code(lines, pool):
    labels = collect_labels(lines)
    pc = 0
    output = []

    for line in lines:
        if line.endswith(":"):
            continue

        instruction = assemble_instruction(line, pc, labels, pool)
        output.append(instruction)
        pc += len(instruction)

    return b"".join(output)


def method_to_bytes(method, pool):
    code = assemble_method_code(method["lines"], pool)
    code_name_index = pool.utf8("Code")
    name_index = pool.utf8(method["name"])
    descriptor_index = pool.utf8(method["descriptor"])

    code_attribute = (
        u2(method["max_stack"])
        + u2(method["max_locals"])
        + u4(len(code))
        + code
        + u2(0)
        + u2(0)
    )

    return (
        u2(method["access"])
        + u2(name_index)
        + u2(descriptor_index)
        + u2(1)
        + u2(code_name_index)
        + u4(len(code_attribute))
        + code_attribute
    )


def assemble_class(jvm_assembly):
    class_name, methods = parse_assembly(jvm_assembly)
    pool = ConstantPool()

    this_class = pool.class_ref(class_name)
    super_class = pool.class_ref("java/lang/Object")

    for method in methods:
        method_to_bytes(method, pool)

    methods_bytes = [method_to_bytes(method, pool) for method in methods]

    return (
        u4(0xCAFEBABE)
        + u2(0)
        + u2(49)
        + pool.to_bytes()
        + u2(0x0021)
        + u2(this_class)
        + u2(super_class)
        + u2(0)
        + u2(0)
        + u2(len(methods_bytes))
        + b"".join(methods_bytes)
        + u2(0)
    )
