# GMLang Compiler

GMLang là một ngôn ngữ lập trình nhỏ được xây dựng cho bài tập lớn môn Nguyên lý ngôn ngữ lập trình. Repo này hiện thực một compiler cơ bản nhưng đầy đủ pipeline:

```text
Mã nguồn GMLang
-> Lexer
-> Parser / AST
-> Semantic Analyzer
-> JVM Code Generator
-> File .class
-> Chạy trên JVM
```

Compiler được viết bằng Python và có thể biên dịch chương trình GMLang thành file `.class` để chạy bằng Java Virtual Machine.

## Yêu Cầu Môi Trường

Cần có:

- Python 3
- Java Runtime, lệnh `java` có trong PATH

Kiểm tra:

```powershell
python --version
java -version
```

File `.class` được tạo trực tiếp bởi [code/classfile.py](code/classfile.py).

## Cấu Trúc Project

```text
.
|-- code/
|   |-- token.py       # Định nghĩa Token và TokenType
|   |-- lexer.py       # Tách mã nguồn thành token
|   |-- ast.py         # Định nghĩa các node AST
|   |-- parser.py      # Recursive descent parser
|   |-- semantic.py    # Kiểm tra ngữ nghĩa, kiểu dữ liệu, scope, symbol table
|   |-- codegen.py     # Sinh JVM instruction dạng text
|   |-- classfile.py   # Đóng gói JVM instruction thành file .class
|   |-- compiler.py    # CLI compiler chính
|   |-- main.py        # File demo/debug
|   |-- errors.py      # Các class lỗi dùng chung
|   `-- explain.qmd    # Tài liệu giải thích code
|-- example.gm         # Chương trình GMLang mẫu
|-- specification.qmd  # Đặc tả ngôn ngữ
|-- specification.pdf  # Bản PDF của đặc tả
`-- README.md
```

## GMLang Hỗ Trợ Gì?

Ví dụ chương trình:

```gmlang
begin
{
    int x = 10;
    auto y = 3.14;

    for (x = 0 to 5 step 1) {
        print(x);
    }

    if (x > 5) then {
        print(x);
    } else {
        print(0);
    }
}
end
```

GMLang hiện hỗ trợ:

- Kiểu dữ liệu: `int`, `bool`, `float`, `string`, `auto`
- Khai báo biến
- Gán biến
- `print(...)`
- `input(...)`
- `if / elseif / else`
- `for`
- `do while`
- Block `{ ... }`
- Toán tử số học: `+`, `-`, `*`, `/`
- Toán tử so sánh: `>`, `>=`, `<`, `<=`, `==`
- Toán tử logic: `&&`, `||`, `!`
- Comment một dòng `// ...`
- Comment nhiều dòng `/* ... */`

## Cách Chạy Nhanh

Từ thư mục gốc của project, chạy:

```powershell
python code\compiler.py example.gm --run
```

Lệnh này sẽ:

1. Đọc file `example.gm`
2. Phân tích từ vựng
3. Phân tích cú pháp
4. Kiểm tra ngữ nghĩa
5. Sinh JVM code
6. Tạo `build/Main.class`
7. Gọi JVM để chạy chương trình

Output với `example.gm` hiện tại:

```text
Wrote build\Main.j
Wrote build\Main.class
0
1
2
3
4
5
6
```

## Compile Mà Không Chạy

Nếu chỉ muốn compile ra file output:

```powershell
python code\compiler.py example.gm
```

Compiler sẽ tạo:

```text
build/Main.j
build/Main.class
```

Ý nghĩa:

- `Main.j`: mã JVM dạng text, dùng để đọc/debug.
- `Main.class`: bytecode thật, chạy được bằng JVM.

Chạy file `.class` thủ công:

```powershell
java -cp build Main
```

## Đổi Thư Mục Output

Dùng `--out-dir`:

```powershell
python code\compiler.py example.gm --run --out-dir build_demo
```

Output:

```text
build_demo/Main.j
build_demo/Main.class
```

Chạy thủ công:

```powershell
java -cp build_demo Main
```

## Đổi Tên Class Sinh Ra

Mặc định compiler tạo class tên `Main`. Có thể đổi bằng `--class-name`:

```powershell
python code\compiler.py example.gm --class-name Demo --out-dir build_demo
```

Output:

```text
build_demo/Demo.j
build_demo/Demo.class
```

Chạy:

```powershell
java -cp build_demo Demo
```

## Ví Dụ Với input(...)

Tạo file `example_input.gm`:

```gmlang
begin
{
    int x;
    input(x);
    print(x + 1);
}
end
```

Compile:

```powershell
python code\compiler.py example_input.gm --out-dir build_input
```

Chạy và nhập từ bàn phím:

```powershell
java -cp build_input Main
```

Nếu nhập:

```text
41
```

chương trình in:

```text
42
```

Có thể truyền input trực tiếp trong PowerShell:

```powershell
Write-Output 41 | java -cp build_input Main
```

## File main.py Dùng Để Làm Gì?

[code/main.py](code/main.py) là file demo/debug. File này hard-code một chương trình GMLang trong biến `code`, sau đó in AST và JVM code ra terminal.

Chạy:

```powershell
python code\main.py
```

Dùng `main.py` khi muốn xem nhanh AST hoặc codegen.

Dùng `compiler.py` khi muốn compile file `.gm` thật.

## Flow Chi Tiết

### 1. Lexer

[code/lexer.py](code/lexer.py) đọc chuỗi source và tạo token.

Ví dụ:

```gmlang
int x = 10;
```

được tách thành:

```text
INT, IDENTIFIER(x), ASSIGN, INT_LITERAL(10), SEMICOLON
```

### 2. Parser

[code/parser.py](code/parser.py) nhận token và tạo AST.

Ví dụ:

```gmlang
x = 1 + 2;
```

thành AST dạng:

```text
Assign
  name: x
  expr:
    BinOp +
      Num 1
      Num 2
```

### 3. Semantic Analyzer

[code/semantic.py](code/semantic.py) kiểm tra:

- Biến đã khai báo chưa
- Biến có bị khai báo trùng không
- Scope có hợp lệ không
- Kiểu dữ liệu có đúng không
- `auto` suy luận ra kiểu nào
- Điều kiện `if`, `elseif`, `while` có phải `bool` không

Nếu sai, compiler báo lỗi kèm dòng/cột.

Ví dụ:

```gmlang
begin
{
    int x;
    x = true;
}
end
```

báo lỗi:

```text
Cannot assign bool to int at 4:9
```

### 4. Code Generator

[code/codegen.py](code/codegen.py) sinh JVM instruction dạng text.

Ví dụ:

```gmlang
int x = 1 + 2;
```

sinh:

```text
iconst_1
iconst_2
iadd
istore 1
```

### 5. Class File Assembler

[code/classfile.py](code/classfile.py) đóng gói JVM instruction thành file `.class` thật.

File `.class` này có thể chạy bằng:

```powershell
java -cp build Main
```

## Lỗi Thường Gặp

### Chạy `python main.py` không tạo build

`main.py` chỉ dùng để debug và in output ra terminal. Để tạo `build/Main.class`, chạy:

```powershell
python code\compiler.py example.gm
```

### Không tìm thấy file source

Hãy đảm bảo đang đứng ở thư mục gốc project.

Đúng:

```powershell
python code\compiler.py example.gm --run
```

Nếu đang ở trong thư mục `code/`, dùng:

```powershell
python compiler.py ..\example.gm --run
```

### Java không chạy

Kiểm tra:

```powershell
java -version
```

Nếu lệnh này lỗi, cần cài Java hoặc thêm Java vào PATH.

## Trạng Thái Hiện Tại

Project đã khớp phần lớn specification:

- Có lexer
- Có parser và AST
- Có semantic analyzer
- Có symbol table
- Có type inference
- Có JVM code generation
- Có sinh `.class`
- Có chạy trực tiếp trên JVM

Một số giới hạn hiện tại:

- `String == String` chưa so sánh nội dung bằng `.equals`.
- `&&` và `||` chưa short-circuit.
- `for` phù hợp nhất với `step` dương.
- Error recovery mới ở mức cơ bản.
- Chưa có test suite riêng.

## Các Lệnh Hay Dùng

Compile và chạy:

```powershell
python code\compiler.py example.gm --run
```

Compile không chạy:

```powershell
python code\compiler.py example.gm
```

Chạy `.class` đã build:

```powershell
java -cp build Main
```

Chạy demo/debug:

```powershell
python code\main.py
```
