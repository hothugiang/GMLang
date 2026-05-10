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
iconst_1
iconst_0
if_icmpgt for_positive_step_1
iconst_1
iconst_0
if_icmplt for_negative_step_2
goto for_end_4
for_positive_step_1:
iload 1
iconst_5
if_icmpgt for_end_4
goto for_body_3
for_negative_step_2:
iload 1
iconst_5
if_icmplt for_end_4
for_body_3:
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 1
invokevirtual java/io/PrintStream/println(I)V
iload 1
iconst_1
iadd
istore 1
goto for_start_0
for_end_4:
iload 1
iconst_5
if_icmpgt cmp_true_7
iconst_0
goto cmp_end_8
cmp_true_7:
iconst_1
cmp_end_8:
ifeq if_next_6
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 1
invokevirtual java/io/PrintStream/println(I)V
goto if_end_5
if_next_6:
iload 1
iconst_3
if_icmpgt cmp_true_10
iconst_0
goto cmp_end_11
cmp_true_10:
iconst_1
cmp_end_11:
ifeq if_next_9
getstatic java/lang/System/out Ljava/io/PrintStream;
iconst_1
invokevirtual java/io/PrintStream/println(I)V
goto if_end_5
if_next_9:
getstatic java/lang/System/out Ljava/io/PrintStream;
iconst_2
invokevirtual java/io/PrintStream/println(I)V
if_end_5:
do_start_12:
iload 1
iconst_1
iadd
istore 1
iload 1
bipush 10
if_icmplt cmp_true_13
iconst_0
goto cmp_end_14
cmp_true_13:
iconst_1
cmp_end_14:
ifne do_start_12
return
.end method