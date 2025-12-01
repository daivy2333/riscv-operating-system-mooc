GDB 对于操作系统开发至关重要，尤其是搭配 QEMU 调试 RISC-V 内核。下面给你一份**专为 RISC-V 内核调试定制的、零基础友好的 GDB 实战速成指南**，只讲你马上能用的核心操作。

---

###  一、准备工作：确保调试环境可用

1. **编译时加调试信息**（关键！）
   ```bash
   # 在你的 Makefile 中，确保 CFLAGS 包含 -g -O0
   CFLAGS = -march=rv64imac -mabi=lp64 -static -g -O0 -Wall
   ```
   - `-g`：生成调试信息（让 GDB 知道哪行 C 对应哪条汇编）
   - `-O0`：关闭优化（避免代码顺序错乱，方便单步）

2. **重新编译内核**
   ```bash
   make clean
   make
   # 应生成 kernel.elf（含调试信息）和 kernel.bin
   ```

---

###  二、GDB + QEMU 联合调试（标准流程）

####  步骤 1：启动 QEMU 并监听 GDB 端口（**不运行，只等连接**）
```bash
qemu-system-riscv64 \
    -machine virt \
    -bios none \
    -kernel kernel.elf \
    -nographic \
    -S -gdb tcp::1234
```
- `-S`：启动后**暂停 CPU**，等待 GDB 连接。
- `-gdb tcp::1234`：在 1234 端口等 GDB。

 此时终端卡住——QEMU 已启动，但 CPU 停在第一条指令（0x80200000 附近），**等你调试**。

---

####  步骤 2：另开终端，启动 GDB 并连接
```bash
# 启动 GDB（注意：要用 multiarch 支持 RISC-V）
gdb-multiarch kernel.elf
```

在 GDB 交互界面中输入：
```gdb
(gdb) target remote :1234       # 连接 QEMU
(gdb) set arch riscv:rv64       # 显式指定架构（若自动识别失败）
(gdb) load                      # 将 kernel.elf 加载到 QEMU 内存（重要！）
(gdb) break main                # 在 C 函数 main 处设断点
(gdb) continue                  # 让 QEMU 继续运行，直到 main
```

>  `load` 是关键！因为 `-kernel` 只加载二进制，GDB 需通过 `load` 把含调试符号的 `.elf` 同步过去。

---

###  三、GDB 最常用 10 个命令（RISC-V 内核调试专用）

| 命令 | 作用 | 示例 |
|------|------|------|
| `break main` 或 `b main` | 在 `main` 函数设断点 | `b trap.c:15` |
| `continue` 或 `c` | 继续运行直到断点 | `c` |
| `step` 或 `s` | 单步进入（进函数） | `s` |
| `next` 或 `n` | 单步跳过（不进函数） | `n` |
| `print x` 或 `p x` | 打印变量 `x` 的值 | `p count` |
| `info registers` 或 `i r` | 查看所有寄存器 | `i r a0`（只看 a0）|
| `x/10i $pc` | 查看当前 PC 附近 10 条汇编 | `x/5i $pc` |
| `disassemble main` | 反汇编 `main` 函数 | `disas start` |
| `backtrace` 或 `bt` | 查看函数调用栈 | `bt` |
| `quit` 或 `q` | 退出 GDB | `q` |

---

###  四、关键技巧 & 常见问题

####  技巧 1：查看 `start.S` 启动代码
```gdb
(gdb) layout asm    # 分屏显示汇编（需支持 TUI）
(gdb) stepi         # 单步执行汇编指令（比 `s` 更底层）
(gdb) info registers ra, sp, gp   # 只看关键寄存器
```

####  技巧 2：查看内存内容
```gdb
(gdb) x/16wx 0x80200000    # 从 0x80200000 开始，16 个 4 字节字（小端）
(gdb) x/10i _start         # 反汇编 _start 符号处的 10 条指令
```

####  问题：`break main` 提示 “No symbol 'main' in current context”
→ 原因：还没跑到 `main` 的代码段，或符号未加载。  
 解决：
```gdb
(gdb) info functions main   # 先查符号是否存在
(gdb) symbol-file kernel.elf # 重新加载符号（若丢失）
```

####  问题：`step` 直接跑飞了
→ 原因：跳过了启动汇编，直接进 C 了。  
解决：先在 `_start` 处断点：
```gdb
(gdb) break _start
(gdb) continue
(gdb) stepi   # 然后用 stepi 单步汇编
```

---

###  五、实战小练习（5 分钟上手）

1. 在 `main.c` 中加一个全局变量：
   ```c
   int count = 0;
   ```
2. 在 `main` 函数循环中加：
   ```c
   count++;
   ```
3. 重新 `make`
4. 启动 GDB 调试：
   ```gdb
   (gdb) b main
   (gdb) c
   (gdb) p count    # 应该是 0
   (gdb) n          # 执行 count++
   (gdb) p count    # 应该是 1
   ```

---

###  推荐速查表

- [GDB Cheat Sheet (PDF)](https://kapeli.com/cheat_sheets/GDB.docset/Contents/Resources/Documents/index)
- [RISC-V GDB 调试官方文档](https://sourceware.org/gdb/current/onlinedocs/gdb/RISC_002dV.html)

