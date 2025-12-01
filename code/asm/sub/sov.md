
这个错误是因为你直接用 gcc 编译裸机汇编代码时遇到了问题。错误主要有两个原因：

1. `_start` 符号冲突：链接器默认会提供一个 `_start` 入口点，而你的代码中也定义了 `_start`
2. `main` 未定义：gcc 默认期望找到一个 `main` 函数作为入口点

对于这种裸机汇编代码，你应该使用 `as` 和 `ld` 而不是 `gcc`。正确的编译步骤是：

```bash
# 汇编
riscv64-linux-gnu-as -o sub.o test.s

# 链接
riscv64-linux-gnu-ld -o sub sub.o

# 查看反汇编
riscv64-linux-gnu-objdump -d sub
```
or
riscv64-unknown-elf-as -o sub.o test.s
riscv64-unknown-elf-ld -o sub sub.o
riscv64-unknown-elf-objdump -d sub

如果你确实想用 gcc，需要修改代码：

1. 将 `_start` 改为 `main`
2. 添加适当的返回指令

修改后的代码应该是：
```riscv
	.text
	.global main

main:
	li x6, -1
	li x7, -2
	sub x5, x6, x7
	li a0, 0  # 返回值
	ret       # 返回
```

但考虑到这是裸机代码，建议使用第一种方法（as + ld），这样更符合裸机编程的特点。