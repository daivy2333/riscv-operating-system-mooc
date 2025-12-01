你遇到的这个错误：

```
cc1: error: unknown cpu 'haswell' for '-mtune'
```

说明 **RISC-V 的交叉编译器 `riscv64-unknown-elf-gcc` 被错误地注入了 x86_64 的编译选项**（比如 `-mtune=haswell`、`-march=nocona`），这些是 Intel CPU 的优化参数，**完全不适用于 RISC-V 编译器**，因此报错。

---

### 🔍 根本原因分析

从你的编译命令可以看出：

```bash
riscv64-unknown-elf-gcc \
  -march=nocona -mtune=haswell -ftree-vectorize -fPIC -fstack-protector-strong \
  -fno-plt -O2 -ffunction-sections -pipe \
  -isystem /home/daivy/miniconda3/include \
  -I/home/daivy/miniconda3/targets/x86_64-linux/include \
  -L/home/daivy/miniconda3/targets/x86_64-linux/lib ...
```

这些 `-march=nocona`、`-mtune=haswell`、`-isystem .../miniconda3/include` 等都是 **Conda 环境干扰**导致的！

你当前的 shell 处于 **`(base)` Conda base 环境**，而 Conda 可能通过 `CFLAGS`、`CPPFLAGS`、`LDFLAGS` 等环境变量注入了 host（x86_64 Linux）的编译参数，污染了交叉编译过程。

> ✅ `riscv64-unknown-elf-gcc` 是交叉编译工具链，**绝不应混用 host 系统（x86）的头文件路径和优化参数**。

---

### ✅ 解决方案（任选其一）

#### ✅ 方法 1：**退出 Conda 环境**（推荐临时做法）

```bash
conda deactivate
# 如果还在 (base)，再执行一次：
conda deactivate
```

确认提示符不再显示 `(base)`：

```bash
echo $CONDA_DEFAULT_ENV  # 应为空或显示 none
```

然后重试编译：

```bash
cd ~/projects/riscv-operating-system-mooc/code/os
make clean
make
```

> 多数情况下，仅 `conda deactivate` 即可解决。

---

#### ✅ 方法 2：**清除污染的环境变量**（如果不想退出 Conda）

在编译前清空 Conda 注入的变量：

```bash
unset CFLAGS CPPFLAGS CXXFLAGS LDFLAGS
make clean
make
```

或更彻底地（仅本次命令）：

```bash
env -i PATH="$PATH" HOME="$HOME" USER="$USER" make
```

> `env -i` 表示“清空所有环境变量”，只保留你显式指定的几个关键变量（PATH 等）。

---

#### ✅ 方法 3：**修改项目 Makefile / common.mk（治本）**

检查 `common.mk` 或 `Makefile` 中是否**未重置**标准编译变量。理想情况下，交叉编译项目应**显式定义纯净的 `CFLAGS`**，例如：

```makefile
CROSS_COMPILE = riscv64-unknown-elf-
CC = $(CROSS_COMPILE)gcc
AS = $(CROSS_COMPILE)as
LD = $(CROSS_COMPILE)ld

# 清空默认 CFLAGS，避免继承污染
CFLAGS = -march=rv32g -mabi=ilp32 -Wall -g -O2 -fno-builtin -nostdlib
```

在 `common.mk` 中搜索 `CFLAGS ?=` 或 `CFLAGS +=` —— 如果是 `+=`，就可能叠加了 Conda 的值。

可临时在 `common.mk` 开头加一句强制覆盖：

```makefile
override CFLAGS := -march=rv32g -mabi=ilp32 -Wall -g -O2 -fno-builtin -nostdlib
override LDFLAGS :=
```

---

### 🚨 额外注意：目标架构是 RV32，但你用了 `riscv64-unknown-elf-gcc`

项目中使用的是：

```bash
-march=rv32g -mabi=ilp32
```

→ 说明是 **32 位 RISC-V**（rv32）。

而 `gcc-riscv64-unknown-elf` 默认是为 64 位设计的，**虽通常兼容 32 位编译**（只要指定 `-march=rv32...`），但某些旧版本可能不支持。

✅ 检查你的工具链是否支持 RV32：

```bash
riscv64-unknown-elf-gcc -march=rv32i -S -o /dev/null -xc /dev/null && echo "OK" || echo "FAIL"
```

如果报错（如 `unrecognized emulation mode`），则需安装 **完整版工具链**：

```bash
# Ubuntu 20.04/22.04 推荐（含 rv32 支持）
sudo apt install gcc-riscv64-unknown-elf binutils-riscv64-unknown-elf

# 或使用 SiFive 官方预编译（更可靠）：
# https://www.sifive.com/software
```

> 实际上 Debian/Ubuntu 的 `gcc-riscv64-unknown-elf` 包默认支持 rv32（通过 multilib），99% 情况下没问题 —— 你当前问题主因还是 **Conda 污染**。

---

### ✅ 快速验证修复成功

```bash
conda deactivate
cd ~/projects/riscv-operating-system-mooc/code/os/00-bootstrap
make clean
make
```

应看到类似：

```
riscv64-unknown-elf-gcc -march=rv32g -mabi=ilp32 -c -o out/start.o start.S
riscv64-unknown-elf-ld -T linker.ld -o out/bootstrap.elf out/start.o
...
```

无 `haswell`/`nocona` 即成功 ✅

需要我帮你写一个「安全编译脚本」（自动隔离 Conda）？