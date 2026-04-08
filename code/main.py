from lexer import Lexer

# Code test (giống ngôn ngữ bạn thiết kế)
code = '''
begin
{
    int x = 10;
    float y = 3.14;
    string s = "hello";

    // loop
    for i = 0 to 5 step 1 {
        print(i);
    }

    // else
    if(x > 5) then {
        print(x);
    } elseif (x > 3) {
        print(1);
    } else {
        print(2);
    }
    
end
'''

# Khởi tạo lexer
lexer = Lexer(code)

# Lấy từng token
while True:
    token = lexer.get_next_token()
    print(token)

    if token.type.name == "EOF":
        break