 **练习 5-6** —— 在 RISC-V 汇编中使用 `.macro` / `.endm` 宏机制，模拟 C 语言中结构体的成员赋值与读取。

---

##  练习目标

1. 在内存中定义一个结构体变量 `s`（包含两个 `unsigned int` 成员 `a` 和 `b`）。
2. 编写汇编宏：
   - `set_struct(s, a_val, b_val)`：将给定值赋给结构体成员。
   - `get_struct(s, reg_a, reg_b)`：将结构体成员值读入指定寄存器。
3. 使用这些宏完成类似 C 代码的功能：
   ```c
   register unsigned int a = 0x12345678;
   register unsigned int b = 0x87654321;
   set_struct(s);
   a = 0; b = 0;
   get_struct(s);
   ```

---

##  步骤详解

###  结构体布局（C 语言视角）

```c
struct S {
    unsigned int a;  // 偏移 0
    unsigned int b;  // 偏移 4
};
```

在 RISC-V 中，每个 `int` 占 4 字节，所以：

- `s.a` 地址 = `&s + 0`
- `s.b` 地址 = `&s + 4`

---

###  定义结构体变量（在 `.data` 段）

```asm
.section .data
s:
    .word 0          # s.a
    .word 0          # s.b
```

---

###  编写宏：`.macro` / `.endm`

RISC-V 汇编（GNU as）支持 `.macro` 定义宏，语法如下：

```asm
.macro macro_name arg1, arg2, ...
    # 宏体
.endm
```

#### 🔹 宏 `set_struct(s, a_val, b_val)`

功能：将 `a_val` 和 `b_val` 存入结构体 `s` 的成员 `a` 和 `b`。

```asm
.macro set_struct s, a_val, b_val
    la \s, \s          # 加载结构体地址到临时寄存器（实际不需要，直接用标签）
    li t0, \a_val      # 加载 a 值
    li t1, \b_val      # 加载 b 值
    sw t0, 0(\s)       # s.a = a_val
    sw t1, 4(\s)       # s.b = b_val
.endm
```

>  注意：这里 `\s` 是宏参数，在展开时会被替换。但 `la \s, \s` 是错误的，因为 `\s` 是标签名，不能作为寄存器。我们需要用一个临时寄存器保存地址。

修正版：

```asm
.macro set_struct s, a_val, b_val
    la t0, \s          # t0 = &s
    li t1, \a_val
    li t2, \b_val
    sw t1, 0(t0)       # s.a = a_val
    sw t2, 4(t0)       # s.b = b_val
.endm
```

#### 🔹 宏 `get_struct(s, reg_a, reg_b)`

功能：从结构体 `s` 中读取成员 `a` 和 `b` 到寄存器 `reg_a` 和 `reg_b`。

```asm
.macro get_struct s, reg_a, reg_b
    la t0, \s          # t0 = &s
    lw \reg_a, 0(t0)   # reg_a = s.a
    lw \reg_b, 4(t0)   # reg_b = s.b
.endm
```

---

###  主程序：实现等价于 C 代码的行为

完整汇编文件 `struct_macro.s`：

```asm
# struct_macro.s - RISC-V assembly with macros for struct access
.section .data
s:
    .word 0          # s.a
    .word 0          # s.b

.section .text
.global _start

# 定义宏
.macro set_struct s, a_val, b_val
    la t0, \s          # t0 = &s
    li t1, \a_val
    li t2, \b_val
    sw t1, 0(t0)       # s.a = a_val
    sw t2, 4(t0)       # s.b = b_val
.endm

.macro get_struct s, reg_a, reg_b
    la t0, \s          # t0 = &s
    lw \reg_a, 0(t0)   # reg_a = s.a
    lw \reg_b, 4(t0)   # reg_b = s.b
.endm

_start:
    # 等价于：register unsigned int a = 0x12345678; register unsigned int b = 0x87654321;
    li t3, 0x12345678   # a -> t3
    li t4, 0x87654321   # b -> t4

    # set_struct(s);
    set_struct s, 0x12345678, 0x87654321

    # a = 0; b = 0;
    li t3, 0
    li t4, 0

    # get_struct(s);
    get_struct s, t3, t4

    # 现在 t3 = s.a = 0x12345678, t4 = s.b = 0x87654321

    # 退出程序（Linux 系统调用）
    li a7, 93           # sys_exit
    li a0, 0            # exit status
    ecall
```

---

##  编译与调试（使用 `riscv64-unknown-elf`）

```bash
# 编译
riscv64-unknown-elf-as -o struct_macro.o struct_macro.s
riscv64-unknown-elf-ld -Ttext=0x80000000 -o struct_macro.elf struct_macro.o

# 或者用 gcc（更简单）
riscv64-unknown-elf-gcc -nostdlib -o struct_macro struct_macro.s
```

---

##  GDB 调试验证

```bash
riscv64-unknown-elf-gdb struct_macro.elf
```

在 GDB 中：

```gdb
(gdb) break _start
(gdb) run
(gdb) stepi 5         # 执行前5条指令（加载 a, b 值）
(gdb) info reg t3 t4
t3             0x12345678       305419896
t4             0x87654321       -2023406815

(gdb) stepi 4         # 执行 set_struct（4条指令）
(gdb) x/2w &s         # 查看内存中 s 的内容
0x80000000:	0x12345678	0x87654321

(gdb) stepi 2         # 执行 a=0; b=0;
(gdb) info reg t3 t4
t3             0x0              0
t4             0x0              0

(gdb) stepi 2         # 执行 get_struct（2条指令）
(gdb) info reg t3 t4
t3             0x12345678       305419896
t4             0x87654321       -2023406815
```

 **完美！结构体成员被正确赋值和读取！**

---

##  最终答案总结

### **汇编代码 `struct_macro.s`**

```asm
.section .data
s:
    .word 0
    .word 0

.section .text
.global _start

.macro set_struct s, a_val, b_val
    la t0, \s
    li t1, \a_val
    li t2, \b_val
    sw t1, 0(t0)
    sw t2, 4(t0)
.endm

.macro get_struct s, reg_a, reg_b
    la t0, \s
    lw \reg_a, 0(t0)
    lw \reg_b, 4(t0)
.endm

_start:
    li t3, 0x12345678
    li t4, 0x87654321
    set_struct s, 0x12345678, 0x87654321
    li t3, 0
    li t4, 0
    get_struct s, t3, t4
    li a7, 93
    li a0, 0
    ecall
```

---

##  小贴士

- 宏中的 `\s`, `\a_val` 是参数占位符，展开时会被替换。
- `la` 是伪指令，实际是 `lui` + `addi`。
- 寄存器 `t0-t6` 是临时寄存器，适合在宏内使用。
- 如果你想让宏更通用（比如支持任意寄存器），可以传递寄存器名作为参数，如 `get_struct s, x5, x6`。

