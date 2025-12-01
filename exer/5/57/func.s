.section .text
.global _start

# unsigned int square(unsigned int i)
# 参数: a0 = i
# 返回: a0 = i * i
square:
    mul a0, a0, a0
    ret

# unsigned int sum_squares(unsigned int i)
# 参数: a0 = i
# 返回: a0 = 1^2 + 2^2 + ... + i^2
sum_squares:
    # 保存 callee-saved 寄存器 s0 (用于保存 i) 和 s1 (用于保存 sum)
    addi sp, sp, -16
    sd s0, 0(sp)
    sd s1, 8(sp)

    mv s0, a0           # s0 = i
    li s1, 0            # s1 = sum = 0
    li t0, 1            # t0 = j = 1

    loop:
        bgt t0, s0, end     # if j > i, exit loop

        mv a0, t0           # a0 = j
        jal ra, square      # call square(j); result in a0

        add s1, s1, a0      # sum += square(j)
        addi t0, t0, 1      # j++
        j loop

    end:
        mv a0, s1           # return sum

        # 恢复 callee-saved 寄存器
        ld s1, 8(sp)
        ld s0, 0(sp)
        addi sp, sp, 16
        ret

# 主程序入口
_start:
    li a0, 3            # argument: i = 3
    jal ra, sum_squares # call sum_squares(3); result in a0

    # exit(0)
    li a7, 93           # sys_exit
    li a0, 0            # exit status
    ecall