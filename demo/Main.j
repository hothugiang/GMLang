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

iconst_3
istore 1
iconst_0
istore 2
ldc 2.5
fstore 3
iconst_1
istore 4
ldc "GMLang"
astore 5
iload 1
bipush 7
iadd
istore 6
getstatic java/lang/System/out Ljava/io/PrintStream;
aload 5
invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 1
invokevirtual java/io/PrintStream/println(I)V
getstatic java/lang/System/out Ljava/io/PrintStream;
fload 3
invokevirtual java/io/PrintStream/println(F)V
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 4
invokevirtual java/io/PrintStream/println(Z)V
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 6
invokevirtual java/io/PrintStream/println(I)V
iload 6
bipush 10
if_icmpge cmp_true_2
iconst_0
goto cmp_end_3
cmp_true_2:
iconst_1
cmp_end_3:
ifeq if_next_1
getstatic java/lang/System/out Ljava/io/PrintStream;
ldc "total >= 10"
invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V
goto if_end_0
if_next_1:
iload 6
iconst_5
if_icmpeq cmp_true_5
iconst_0
goto cmp_end_6
cmp_true_5:
iconst_1
cmp_end_6:
ifeq if_next_4
getstatic java/lang/System/out Ljava/io/PrintStream;
ldc "total == 5"
invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V
goto if_end_0
if_next_4:
getstatic java/lang/System/out Ljava/io/PrintStream;
ldc "small"
invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V
if_end_0:
iconst_0
istore 2
for_start_7:
iconst_1
iconst_0
if_icmpgt for_positive_step_8
iconst_1
iconst_0
if_icmplt for_negative_step_9
goto for_end_11
for_positive_step_8:
iload 2
iconst_3
if_icmpgt for_end_11
goto for_body_10
for_negative_step_9:
iload 2
iconst_3
if_icmplt for_end_11
for_body_10:
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 2
invokevirtual java/io/PrintStream/println(I)V
iload 2
iconst_1
iadd
istore 2
goto for_start_7
for_end_11:
do_start_12:
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 1
invokevirtual java/io/PrintStream/println(I)V
iload 1
iconst_1
isub
istore 1
iload 1
iconst_0
if_icmpgt cmp_true_13
iconst_0
goto cmp_end_14
cmp_true_13:
iconst_1
cmp_end_14:
ifne do_start_12
return
.end method