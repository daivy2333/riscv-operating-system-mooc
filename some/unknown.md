
这两个工具链的主要区别在于目标系统和用途：

1. `riscv64-unknown-elf-gcc` (裸机工具链)
- 目标系统：裸机（bare-metal）系统，没有操作系统
- 使用场景：
  - 开发操作系统内核
  - 编写引导程序（bootloader）
  - 嵌入式系统开发
  - 固件开发
- 特点：
  - 不包含系统调用相关的库
  - 不依赖 Linux 系统调用
  - 生成的代码更精简
  - 适合底层系统开发

2. `riscv64-linux-gnu-gcc` (Linux工具链)
- 目标系统：Linux 系统
- 使用场景：
  - 开发 Linux 应用程序
  - Linux 系统上的用户空间程序
- 特点：
  - 包含完整的 C 标准库
  - 支持 Linux 系统调用
  - 包含动态链接支持
  - 可以使用 glibc

在你的情况下，由于你在开发操作系统相关的代码（从之前的路径可以看出是操作系统课程），应该使用 `riscv64-unknown-elf-gcc`，因为：
1. 你在开发底层系统代码
2. 不需要 Linux 系统支持
3. 需要更直接的控制硬件

所以正确的编译命令应该是：
```bash
riscv64-unknown-elf-as -o sub.o test.s
riscv64-unknown-elf-ld -o sub sub.o
riscv64-unknown-elf-objdump -d sub
```