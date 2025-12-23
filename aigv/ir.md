<PIR>
<META>...</META>
<UNITS>...</UNITS>
<GRAPH>...</GRAPH>
<SYMBOLS>...</SYMBOLS>
<LAYOUT>...</LAYOUT>
<CODE>...</CODE>
</PIR>
<META>
name:aigv
root:/home/daivy/projects/...
profile:os-riscv
lang:C,ASM,LD,Python
</META>
<UNITS>
u0:core/init.c type=C arch=core
u1:mm/page.c type=C arch=mm
u2:boot/start.S type=ASM arch=core
u3:os.ld type=LD arch=link
</UNITS>
<GRAPH>
u0->u2
u0->u3
u1->u0
</GRAPH>
<SYMBOLS>
start_kernel:u0 entry
trap_handler:u0 trap
schedule:u0 core
uart_init:u4 driver
_bss_start:u3 ld
_bss_end:u3 ld
</SYMBOLS>
symbol:unit role
<LAYOUT>
ENTRY=_start
BASE=0x80000000
.text:u2 u0
.rodata:u0
.data:u0
.bss:u0
</LAYOUT>
<CODE>
<u2>
csrr t0,mhartid
bnez t0,park
j start_kernel
</u2>

<u0>
void start_kernel(){...}
</u0>
</CODE>
