好的，我们来用 **RISC-V 64 位裸机工具链 `riscv64-unknown-elf-*`** 来解决这两个练习。这个工具链用于编写不依赖操作系统的“裸机”程序（bare-metal），通常用于嵌入式或教学环境。

---

##  练习 5-4：分离32位数的高低16位

给定一个32位数：`0x87654321`

目标：
- C语言实现：将其低16位 (`0x4321`) 和高16位 (`0x8765`) 分别保存到两个独立变量中。
- 汇编语言实现：用 RISC-V 汇编完成相同功能。

---

###  第一步：C语言实现

创建文件 `split_c.c`：

```c
#include <stdio.h>

int main() {
    unsigned int num = 0x87654321;
    unsigned int low16 = num & 0xFFFF;        // 低16位
    unsigned int high16 = (num >> 16) & 0xFFFF; // 高16位

    // 打印结果（可选，裸机环境下可能无法打印）
    // printf("Low 16: 0x%04x\n", low16);
    // printf("High 16: 0x%04x\n", high16);

    return 0;
}
```

>  注意：在裸机环境下，`printf` 不可用。我们只关心寄存器或内存中的值是否正确。

---

###  第二步：汇编语言实现（使用 `riscv64-unknown-elf`）

创建文件 `split_asm.s`：

```asm
# split_asm.s - RISC-V assembly to split 0x87654321 into low/high 16 bits
.section .text
.global _start

_start:
    # 加载 32 位常量 0x87654321 到寄存器 x10
    li x10, 0x87654321      # 实际上，li 只能加载 20 位立即数，所以需要组合

    # 正确方式：用 lui + addi 构造 32 位值
    lui x10, %hi(0x87654321)     # 加载高20位：0x87654
    addi x10, x10, %lo(0x87654321) # 加上低12位：0x321

    # 提取低16位：与 0xFFFF 相与
    li x11, 0xFFFF               # x11 = 0xFFFF
    and x12, x10, x11            # x12 = low16 = 0x4321

    # 提取高16位：右移16位，再与 0xFFFF 相与（虽然此时高16位已无符号扩展，但安全起见）
    srl x13, x10, 16             # x13 = x10 >> 16 = 0x8765
    and x13, x13, x11            # 确保只保留低16位（实际可省略）

    # 程序结束（裸机程序通常不会退出，这里简单停机）
    # 我们可以加一个无限循环，或者直接 halt（如果平台支持）
    # 这里用一个简单的无限循环
loop:
    j loop

    # 或者，如果你的仿真器支持 ecall 退出（如 QEMU），可以用：
    # li a7, 93
    # li a0, 0
    # ecall
```

>  注意：`li` 指令在 RISC-V 中是伪指令，实际由 `lui` + `addi` 组成。对于 32 位常量，必须用 `%hi()` 和 `%lo()` 宏。

---

###  编译和调试（使用 `riscv64-unknown-elf` 工具链）

#### 1. 编译汇编代码：

```bash
riscv64-unknown-elf-as -o split_asm.o split_asm.s
riscv64-unknown-elf-ld -Ttext=0x80000000 -o split_asm.elf split_asm.o
```

> `-Ttext=0x80000000` 指定程序加载地址（常见于 QEMU 或 Spike 仿真器）。

#### 2. 使用 GDB 调试：

```bash
riscv64-unknown-elf-gdb split_asm.elf
```

在 GDB 中：

```gdb
(gdb) break _start
(gdb) run
(gdb) stepi
(gdb) stepi
...
(gdb) info registers x10 x12 x13
```

你应该看到：

- `x10 = 0x87654321`
- `x12 = 0x00004321` （低16位）
- `x13 = 0x00008765` （高16位）

 成功！

---

##  练习 5-5：访问数组元素

给定 C 代码：

```c
int array[2] = {0x11111111, 0xffffffff};
int i = array[0];
int j = array[1];
```

目标：用汇编语言实现相同效果，并验证寄存器值。

---

###  汇编实现

创建文件 `array_access.s`：

```asm
# array_access.s - RISC-V assembly to access array elements
.section .data
array:
    .word 0x11111111
    .word 0xffffffff

.section .text
.global _start

_start:
    # 获取数组基地址（假设在 .data 段，链接时确定）
    la x10, array          # x10 = &array[0]

    # 读取 array[0] -> x11
    lw x11, 0(x10)         # x11 = array[0] = 0x11111111

    # 读取 array[1] -> x12
    lw x12, 4(x10)         # x12 = array[1] = 0xffffffff

    # 程序结束
loop:
    j loop
```

>  注意：
> - `.word` 是 32 位整数，在 RISC-V 中占 4 字节。
> - `lw` 是加载字（load word），从内存加载 32 位数据。
> - 数组索引 `i` 对应偏移 `i * 4` 字节。

---

###  编译和调试

#### 1. 编译：

```bash
riscv64-unknown-elf-as -o array_access.o array_access.s
riscv64-unknown-elf-ld -Ttext=0x80000000 -o array_access.elf array_access.o
```

#### 2. 使用 GDB 调试：

```bash
riscv64-unknown-elf-gdb array_access.elf
```

在 GDB 中：

```gdb
(gdb) break _start
(gdb) run
(gdb) stepi
(gdb) stepi
(gdb) info registers x10 x11 x12
```

你应该看到：

- `x10` = 数组地址（例如 `0x80000000`）
- `x11 = 0x11111111` （i = array[0]）
- `x12 = 0xffffffff` （j = array[1]）

 成功！

---

## 总结答案

### **练习 5-4**

- **C 代码**：使用 `& 0xFFFF` 和 `>> 16` 分离高低16位。
- **汇编代码**：

```asm
_start:
    lui x10, %hi(0x87654321)
    addi x10, x10, %lo(0x87654321)
    li x11, 0xFFFF
    and x12, x10, x11        # low16
    srl x13, x10, 16
    and x13, x13, x11        # high16
    j loop
```

### **练习 5-5**

- **汇编代码**：

```asm
.section .data
array:
    .word 0x11111111
    .word 0xffffffff

.section .text
_start:
    la x10, array
    lw x11, 0(x10)   # i = array[0]
    lw x12, 4(x10)   # j = array[1]
    j loop
```

---

##  补充说明

- 如果你没有仿真器（如 QEMU、Spike），可以在本地用 `gdb` 单步调试，观察寄存器值即可。
- 如果想让程序“退出”，可以添加系统调用（需配合 Linux 环境），但在裸机环境中通常用无限循环或 halt 指令。

