好的，我们来解决练习 5-7。

---

## 练习 5-7：编写汇编程序，使用条件分支指令循环遍历一个字符串数组，获取该字符串的长度

目标：实现与以下 C 代码等价的功能：

```c
char array[] = {'h', 'e', 'l', 'l', 'o', ',', 'w', 'o', 'r', 'l', 'd', '!', '\0'};
int len = 0;
while (array[len] != '\0') {
    len++;
}
```

即：计算以 `\0`（空字符，ASCII 值为 0）结尾的字符串的长度。

---

## ✅ 解题思路

1. 在 `.data` 段定义字符串数组，末尾加 `\0`。
2. 使用一个寄存器（如 `x10`）作为指针，指向当前字符。
3. 使用另一个寄存器（如 `x11`）作为计数器 `len`，初始为 0。
4. 循环：
   - 从内存加载当前字符到临时寄存器。
   - 判断是否为 `\0`（值为 0）。
   - 如果是，跳出循环。
   - 否则，计数器加 1，指针加 1，继续循环。
5. 最终 `x11` 中保存的就是字符串长度。

---

## ✅ 汇编代码实现

创建文件 `strlen.s`：

```asm
# strlen.s - RISC-V assembly to compute string length
.section .data
array:
    .byte 'h', 'e', 'l', 'l', 'o', ',', 'w', 'o', 'r', 'l', 'd', '!', 0

.section .text
.global _start

_start:
    # 初始化
    la x10, array      # x10 = 指向字符串首地址
    li x11, 0          # x11 = len = 0

loop:
    lbu x12, 0(x10)    # 加载当前字节到 x12（无符号加载）
    beq x12, zero, end # 如果 x12 == 0，则跳转到 end
    addi x11, x11, 1   # len++
    addi x10, x10, 1   # 指针后移一位
    j loop             # 跳回循环开始

end:
    # 此时 x11 中存放的是字符串长度（12）

    # 程序结束（Linux 系统调用退出）
    li a7, 93          # sys_exit
    li a0, 0           # exit status
    ecall
```

---

## 🛠️ 编译与调试（使用 riscv64-unknown-elf 工具链）

```bash
# 编译
riscv64-unknown-elf-as -o strlen.o strlen.s
riscv64-unknown-elf-ld -Ttext=0x80000000 -o strlen.elf strlen.o

# 或者用 gcc（推荐，自动处理入口）
riscv64-unknown-elf-gcc -nostdlib -o strlen strlen.s
```

---

## 🔍 GDB 调试验证

```bash
riscv64-unknown-elf-gdb strlen.elf
```

在 GDB 中：

```gdb
(gdb) break _start
(gdb) run
(gdb) stepi 2         # 执行 la 和 li，初始化 x10, x11
(gdb) info reg x10 x11
x10            0x80000000       2147483648
x11            0x0              0

(gdb) break end
(gdb) continue      # 运行到 end 标签
(gdb) info reg x11
x11            0xc              12
```

✅ 成功！字符串长度为 12，符合预期（"hello,world!" 共 12 个字符，不包括末尾 `\0`）。

---

## ✅ 关键指令说明

- `lbu x12, 0(x10)`：从地址 `x10 + 0` 加载一个字节（无符号），存入 `x12`。
- `beq x12, zero, end`：如果 `x12 == 0`，则跳转到 `end`。这是条件分支的核心。
- `addi x11, x11, 1`：计数器加一。
- `addi x10, x10, 1`：指针后移一个字节。
- `j loop`：无条件跳转，形成循环。

---

## ✅ 总结

本练习通过简单的循环和条件分支，实现了字符串长度计算功能。核心在于：

- 使用 `lbu` 逐字节读取字符；
- 使用 `beq` 判断是否遇到 `\0`；
- 使用 `addi` 更新计数器和指针；
- 最终结果保存在寄存器中。

这个程序结构清晰，是学习 RISC-V 条件分支和循环控制的经典示例。

---

如需扩展功能（如支持多字符串、打印长度等），可在此基础上修改。