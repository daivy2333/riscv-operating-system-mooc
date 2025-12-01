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

    # 或者，如果你的仿真器支持 ecall 退出（如 QEMU），可以用：
    li a7, 93
    li a0, 0
    ecall
    