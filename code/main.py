from lexer import Lexer
from parser import Parser

def print_ast(node, indent=0):
    print("  " * indent + type(node).__name__)

    for attr, value in vars(node).items():
        if isinstance(value, list):
            print("  " * (indent+1) + attr + ":")
            for item in value:
                print_ast(item, indent+2)
        elif hasattr(value, "__dict__"):
            print("  " * (indent+1) + attr + ":")
            print_ast(value, indent+2)
        else:
            print("  " * (indent+1) + f"{attr}: {value}")


code = '''
begin
{
    int x = 10;
    auto y = 3.14;

    for (x = 0 to 5 step 1) {
        print(x);
    }

    if (x > 5) then {
        print(x);
    } elseif (x > 3) {
        print(1);
    } else {
        print(2);
    }

    do {
        x = x + 1;
    } while (x < 10);
}
end
'''

lexer = Lexer(code)
parser = Parser(lexer)

ast = parser.parse()

print_ast(ast)