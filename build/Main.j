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
istore 1
for_start_0:
iload 1
iconst_5
if_icmpgt for_end_1
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
if_icmpgt for_positive_step_8
iconst_1
cmp_end_8:
ifeq if_next_6
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 2
invokevirtual java/io/PrintStream/println(I)V
goto if_end_2
if_next_6:
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 1
invokevirtual java/io/PrintStream/println(I)V
if_end_2:
do_start_9:
iload 1
iconst_1
isub
istore 1
iload 1
bipush 10
if_icmplt cmp_true_10
iconst_0
goto cmp_end_14
cmp_true_13:
iconst_1
cmp_end_14:
ifne do_start_12
return
.end method