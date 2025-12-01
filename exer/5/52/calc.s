# calc.s - RISC-V assembly equivalent of the C code

.section .text
.global _start

_start:
    li x11,1
    li x12,2
    li x14,3
    add x10,x11,x12
    sub x13,x10,x14

    li a7,93
    li a0,0

    ecall
    