<pir>
<meta>
name: 1
root: /home/daivy/projects/riscv-operating-system-mooc/exer/7/1
profile: generic
lang: LD,S
</meta>
<units>
u0: linker.ld type=LD role=lib module=1
u1: uart.S type=S role=lib module=1
u2: kernel.S type=S role=lib module=1
</units>
<dependency-pool>
d0: call:u1#done_puts
d1: call:u1#puts_loop
d2: call:u1#uart_init
d3: call:u1#uart_putc
d4: call:u1#uart_puts
d5: call:u1#wait_tx
d6: call:u2#loop
</dependency-pool>
<dependencies>
u1->refs:[d5 d0 d3 d1]
u2->refs:[d2 d4 d6]
</dependencies>
<symbols>
start_kernel:u0 ld_entry
__bss_start:u0 ld_symbol
__bss_end:u0 ld_symbol
_end:u0 ld_symbol
uart_init:u1 label
uart_putc:u1 label
wait_tx:u1 label
uart_puts:u1 label
puts_loop:u1 label
done_puts:u1 label
start_kernel:u2 label
loop:u2 label
hello_str:u2 label
</symbols>
<layout>
ENTRY=start_kernel
SECTIONS=.bss,.data,.rodata,.text
SECTIONS_FROM=u0
</layout>
</pir>