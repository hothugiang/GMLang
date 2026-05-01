.class public Main
.super java/lang/Object

.method public <init>()V
aload_0
invokespecial java/lang/Object/<init>()V
return
.end method

.method public static main([Ljava/lang/String;)V
.limit stack 100
.limit locals 100

bipush 10
istore 1
ldc 3.14
fstore 2
iconst_0
istore 1
for_start_0:
iload 1
iconst_5
if_icmpgt for_end_1
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 1
invokevirtual java/io/PrintStream/println(I)V
iload 1
iconst_1
iadd
istore 1
goto for_start_0
for_end_1:
iload 1
iconst_5
if_icmpgt cmp_true_4
iconst_0
goto cmp_end_5
cmp_true_4:
iconst_1
cmp_end_5:
ifeq if_next_3
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 1
invokevirtual java/io/PrintStream/println(I)V
goto if_end_2
if_next_3:
iload 1
iconst_3
if_icmpgt cmp_true_7
iconst_0
goto cmp_end_8
cmp_true_7:
iconst_1
cmp_end_8:
ifeq if_next_6
getstatic java/lang/System/out Ljava/io/PrintStream;
iconst_1
invokevirtual java/io/PrintStream/println(I)V
goto if_end_2
if_next_6:
getstatic java/lang/System/out Ljava/io/PrintStream;
iconst_2
invokevirtual java/io/PrintStream/println(I)V
if_end_2:
do_start_9:
iload 1
iconst_1
iadd
istore 1
iload 1
bipush 10
if_icmplt cmp_true_10
iconst_0
goto cmp_end_11
cmp_true_10:
iconst_1
cmp_end_11:
ifne do_start_9
return
.end method