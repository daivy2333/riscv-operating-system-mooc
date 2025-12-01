你的情况非常明确：  
你的 `riscv64-unknown-elf-gcc` 是 **单 multilib 构建**（`-print-multi-lib` 只输出 `.`），即：**只支持默认的 `-march` / `-mabi` 组合，不支持任何显式 `-march=...` 指定（哪怕只写 `-mabi=lp64`，GCC 内部也会推导出带 `_z*` 的长串指令集，导致失败）**。

这是 Ubuntu/Debian 包管理器里精简版工具链的典型问题（为减小体积砍掉了 multilib）。

---

###  **终极解决方案：强制使用默认架构（不写任何 `-march`）**

直接运行（**去掉 `-mabi=lp64` 和 `-march`**）：
```bash
riscv64-unknown-elf-gcc -static -o hello hello.c
```

>  这会让 GCC 使用它**唯一支持的默认目标**（通常是 `rv64imac_zicsr_zifencei` 或 `rv64gc`），绕过 multilib 匹配逻辑。

---

###  验证是否成功：
```bash
# 1. 查看生成的 ELF 是不是 RISC-V 64
riscv64-unknown-elf-readelf -h hello | grep -E "Class|Machine"

# 应输出：
#   Class:                             ELF64
#   Machine:                           RISC-V

# 2. 运行
qemu-riscv64 ./hello
# 应输出：Hello World!
```

---

###  补充建议（避免后续踩坑）

1. **永远不要写 `-march=...` 或 `-mabi=...`** —— 除非你知道你的工具链支持。
2. 若仍失败，说明连默认 multilib 都没装全（极少见），请立即切换到 **xPack 工具链**（5 分钟搞定，无坑）：

```bash
# 一键安装 xPack RISC-V GCC（无需 sudo）
cd ~
wget https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/download/v14.2.0-1/xpack-riscv-none-elf-gcc-14.2.0-1-linux-x64.tar.gz
tar -xf xpack-riscv-none-elf-gcc-14.2.0-1-linux-x64.tar.gz
echo 'export PATH="$HOME/xpack-riscv-none-elf-gcc-14.2.0-1/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 然后用新命令编译（注意是 riscv-none-elf-gcc）
riscv-none-elf-gcc -march=rv64imac -mabi=lp64 -static -o hello hello.c
```

>  xPack 工具链全功能、支持所有 `-march`，且与课程完全兼容（课程作者也推荐）。

---

现在请先试：  
```bash
riscv64-unknown-elf-gcc -static -o hello hello.c
```
然后告诉我结果 👇