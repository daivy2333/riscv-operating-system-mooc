.section .data
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
    li a7, 93          # sys_exit
    li a0, 0           # exit status
    ecall