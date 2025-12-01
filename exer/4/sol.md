 Ubuntu 环境只有 RISC-V 64 位工具链（`riscv64-unknown-elf-*`），而没有 `riscv32` 的，那么我们就**直接使用 RISC-V 64 位工具链来完成练习 4-1 和 4-2**。这在学习交叉编译和工具链使用的核心概念上是完全等效的，只是目标架构从 `rv32ima` 变成了 `rv64imac`。

以下是为你量身定制的、基于 `riscv64` 工具链的完整操作指南：

---

##  准备工作

首先，确保你已经安装了 RISC-V 64 位交叉编译工具链。通常安装包名为 `gcc-riscv64-linux-gnu` 或 `gcc-riscv64-unknown-elf`。你可以通过以下命令检查：

```bash
# 检查是否安装了 riscv64 编译器
riscv64-unknown-elf-gcc --version

# 检查 binutils (objdump, readelf, nm 等)
riscv64-unknown-elf-objdump --version

# 检查 qemu-system-riscv64 (用于运行)
qemu-system-riscv64 --version
```

如果没有安装，请先安装：

```bash
sudo apt update
sudo apt install gcc-riscv64-unknown-elf qemu-system-misc
```

---

##  练习 4-1：交叉编译与文件分析 (使用 RISC-V 64)

### 步骤 1: 编写 `hello.c`

创建一个简单的 C 程序：

```bash
nano hello.c
```

粘贴以下代码：

```c
#include <stdio.h>

int main() {
    printf("Hello World!\n");
    return 0;
}
```

保存并退出 (`Ctrl+O`, `Enter`, `Ctrl+X`)。

---

### 步骤 2: 使用 `riscv64-unknown-elf-gcc` 编译为目标文件 `hello.o`

> 注意：这里我们不链接成可执行文件，只生成目标文件（.o），以便后续分析。

```bash
riscv64-unknown-elf-gcc -march=rv64imac -mabi=lp64 -c hello.c -o hello.o
```

- `-march=rv64imac`: 指定目标架构为 RISC-V 64 位，支持整数、乘除、原子、压缩指令。
- `-mabi=lp64`: 指定 64 位 ABI。
- `-c`: 只编译，不链接。
- 这个我的环境用不了
---
### 步骤 3: 查看 `hello.o` 文件头信息

```bash
riscv64-unknown-elf-readelf -h hello.o
```

你会看到类似这样的输出：
```
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              REL (Relocatable file)
  Machine:                           RISC-V
  Version:                           0x1
  Entry point address:               0x0
  Start of program headers:          0 (bytes into file)
  Start of section headers:          488 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           0 (bytes)
  Number of program headers:         0
  Size of section headers:           64 (bytes)
  Number of section headers:         13
  Section header string table index: 12
```

 **关键点**：确认 `Class: ELF64` 和 `Machine: RISC-V`，说明这是一个 64 位 RISC-V 目标文件。

---

### 步骤 4: 查看 `hello.o` 的 Section Header Table

```bash
riscv64-unknown-elf-readelf -S hello.o
```

你会看到各个段（section）的信息，如 `.text`（代码）、`.data`、`.bss`、`.rodata` 等。

 **关键点**：了解目标文件由哪些段组成，以及它们的大小和属性。

---

### 步骤 5: 对 `hello.o` 进行反汇编，并对照源码

```bash
riscv64-unknown-elf-objdump -S hello.o
```

这个命令会将机器码反汇编成汇编指令，并**穿插显示原始的 C 源代码**，方便你对照理解。

你会看到类似这样的输出：

```
Disassembly of section .text:

0000000000000000 <main>:
   0:	1141                	addi	sp,sp,-32
   2:	e426                	sd	s0,24(sp)

好的，接续步骤（仅指令，无解释）：

---

###  练习 4-1（续）

6. 查看符号表：
```bash
riscv64-unknown-elf-readelf -s hello.o
```

7. 查看重定位信息：
```bash
riscv64-unknown-elf-readelf -r hello.o
```

8. 将 `hello.o` 链接成可执行文件（静态链接，无 libc 依赖——需用 `-nostdlib` + 自定义启动）  
   → 但为简化，我们改用新方式：直接编译成可运行的 ELF（动态链接）：

```bash
riscv64-unknown-elf-gcc -march=rv64imac -mabi=lp64 -static -o hello hello.c
```

> `-static`：避免动态链接问题，在 qemu 中更易运行。

9. 查看最终可执行文件 `hello` 的 ELF 头：
```bash
riscv64-unknown-elf-readelf -h hello
```

10. 查看其程序头（Program Headers）：
```bash
riscv64-unknown-elf-readelf -l hello
```

11. 反汇编整个可执行文件（仅 `.text` 段）：
```bash
riscv64-unknown-elf-objdump -d hello
```

12. 查看其依赖（应为空，因 `-static`）：
```bash
riscv64-unknown-elf-readelf -d hello
```

---

##  练习 4-2：运行 RISC-V 64 程序

1. 启动 QEMU 用户模式运行（推荐，轻量）：
```bash
qemu-riscv64 hello
```

> 若提示 `qemu-riscv64` 未找到，安装：
> ```bash
> sudo apt install qemu-user
> ```

2. 或使用系统模式（需提供内核与根文件系统，较复杂）——**跳过，用用户模式即可**。

3. 验证输出为：
```
Hello World!
```

4. （可选）查看运行时寄存器状态（调试）：
```bash
qemu-riscv64 -g 1234 hello &
gdb-multiarch hello
(gdb) target remote :1234
(gdb) info registers
(gdb) stepi
(gdb) quit
kill %1
```
