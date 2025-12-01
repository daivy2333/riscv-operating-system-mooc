# array_access.s - RISC-V assembly to access array elements

.section .data

array:
    .word 0x11111111
    .word 0xffffffff

.section .text
.global _start

_start:

    la x10, array
    lw x11, 0(x10)
    lw x12, 4(x10)

    li a7, 93
    li a0, 0
    ecall
