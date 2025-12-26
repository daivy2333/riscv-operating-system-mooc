<pir>
<meta>
name: 03-contextswitch
root: /home/daivy/projects/riscv-operating-system-mooc/code/os/03-contextswitch
profile: generic
lang: C,H,LD,S
</meta>
<units>
u0: sched.c type=C role=lib module=03-contextswitch
u1: page.c type=C role=lib module=03-contextswitch
u2: platform.h type=H role=lib module=03-contextswitch
u3: entry.S type=S role=lib module=03-contextswitch
u4: os.h type=H role=lib module=03-contextswitch
u5: os.ld type=LD role=lib module=03-contextswitch
u6: uart.c type=C role=lib module=03-contextswitch
u7: start.S type=S role=lib module=03-contextswitch
u8: types.h type=H role=lib module=03-contextswitch
u9: mem.S type=S role=lib module=03-contextswitch
u10: printf.c type=C role=lib module=03-contextswitch
u11: kernel.c type=C role=lib module=03-contextswitch
</units>
<dependency-pool>
d0: call:[f]
d1: call:u11#start_kernel
d2: call:u7#park
d3: include:[os.h]
d4: include:[platform.h]
d5: include:[stdarg.h]
d6: include:[stdlib:c]
d7: include:[types.h]
</dependency-pool>
<dependencies>
u0->refs:[d3]
u1->refs:[d3]
u3->refs:[d0]
u4->refs:[d6 d5 d7 d4]
u6->refs:[d3]
u7->refs:[d1 d2]
u10->refs:[d3]
u11->refs:[d3]
</dependencies>
<symbols>
w_mscratch:u0 func
sched_init:u0 func
schedule:u0 func
task_delay:u0 func
user_task0:u0 func
_clear:u1 func
_is_free:u1 func
_set_flag:u1 func
_is_last:u1 func
_align_page:u1 func
page_init:u1 func
page_free:u1 func
page_test:u1 func
switch_to:u3 label
_start:u5 ld_entry
symbol:u5 ld_symbol
_text_start:u5 ld_symbol
_text_end:u5 ld_symbol
_rodata_start:u5 ld_symbol
_rodata_end:u5 ld_symbol
_data_start:u5 ld_symbol
_data_end:u5 ld_symbol
_bss_start:u5 ld_symbol
_bss_end:u5 ld_symbol
_memory_start:u5 ld_symbol
_memory_end:u5 ld_symbol
_heap_start:u5 ld_symbol
_heap_size:u5 ld_symbol
uart_init:u6 func
uart_putc:u6 func
uart_puts:u6 func
_start:u7 label
park:u7 label
stacks:u7 label
_vsnprintf:u10 func
_vprintf:u10 func
printf:u10 func
panic:u10 func
start_kernel:u11 func
</symbols>
<profiles>
  active: system-c
  c-framework:
    confidence: 0.5
    tags:
      - domain:language-tooling
      - runtime:native
      - stack:c-framework
  system-c:
    confidence: 0.55
    tags:
      - domain:system
      - lang:c
      - runtime:native
    signals:
      - multi-unit
</profiles>
<layout>
ENTRY=_start
SECTIONS=.bss,.data,.rodata,.text
SECTIONS_FROM=u5
</layout>
</pir>