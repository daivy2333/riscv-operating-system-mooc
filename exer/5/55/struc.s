# struct_macro.s - RISC-V assembly with macros for struct access

.section .data
s:
    .word 0          # s.a
    .word 0          # s.b

.section .text
.global _start

.macro set_struct s,a_val,b_val
    la t0, \s          # t0 = &s
    li t1, \a_val
    li t2, \b_val

    sw t1, 0(t0)       # s.a = a_val
    sw t2, 4(t0)       # s.b = b_val

.endm

.macro get_struct s, reg_a, reg_b
    la t0, \s          # t0 = &s
    lw \reg_a, 0(t0)   # reg_a = s.a
    lw \reg_b, 4(t0)   # reg_b = s.b
.endm

_start:
    # 等价于：register unsigned int a = 0x12345678; register unsigned int b = 0x87654321;
    li t3, 0x12345678   # a -> t3
    li t4, 0x87654321   # b -> t4

    # set_struct(s);
    set_struct s, 0x12345678, 0x87654321

    # a = 0; b = 0;
    li t3, 0
    li t4, 0

    # get_struct(s);
    get_struct s, t3, t4

    # 现在 t3 = s.a = 0x12345678, t4 = s.b = 0x87654321

    li a7, 93           # sys_exit
    li a0, 0            # exit status
    ecall