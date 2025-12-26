<pir>
<meta>
name: 02-memanagement
root: /home/daivy/projects/riscv-operating-system-mooc/code/os/02-memanagement
profile: generic
lang: C,H,LD,S
</meta>
<units>
u0: page.c type=C role=lib module=02-memanagement
u1: platform.h type=H role=lib module=02-memanagement
u2: os.h type=H role=lib module=02-memanagement
u3: os.ld type=LD role=lib module=02-memanagement
u4: uart.c type=C role=lib module=02-memanagement
u5: start.S type=S role=lib module=02-memanagement
u6: types.h type=H role=lib module=02-memanagement
u7: mem.S type=S role=lib module=02-memanagement
u8: printf.c type=C role=lib module=02-memanagement
u9: kernel.c type=C role=lib module=02-memanagement
u10: heap.c type=C role=lib module=02-memanagement
</units>
<dependency-pool>
d0: call:u5#park
d1: call:u9#start_kernel
d2: include:[os.h]
d3: include:[platform.h]
d4: include:[stdarg.h]
d5: include:[stdlib:c]
d6: include:[types.h]
</dependency-pool>
<dependencies>
u0->refs:[d2]
u2->refs:[d6 d5 d4 d3]
u4->refs:[d2]
u5->refs:[d1 d0]
u8->refs:[d2]
u9->refs:[d2]
u10->refs:[d2]
</dependencies>
<symbols>
_clear:u0 func
_is_free:u0 func
_set_flag:u0 func
_is_last:u0 func
_align_page:u0 func
page_init:u0 func
page_free:u0 func
page_test:u0 func
_start:u3 ld_entry
symbol:u3 ld_symbol
_text_start:u3 ld_symbol
_text_end:u3 ld_symbol
_rodata_start:u3 ld_symbol
_rodata_end:u3 ld_symbol
_data_start:u3 ld_symbol
_data_end:u3 ld_symbol
_bss_start:u3 ld_symbol
_bss_end:u3 ld_symbol
_memory_start:u3 ld_symbol
_memory_end:u3 ld_symbol
_heap_start:u3 ld_symbol
_heap_size:u3 ld_symbol
uart_init:u4 func
uart_putc:u4 func
uart_puts:u4 func
_start:u5 label
park:u5 label
stacks:u5 label
_vsnprintf:u8 func
_vprintf:u8 func
printf:u8 func
panic:u8 func
start_kernel:u9 func
heap_init:u10 func
malloc:u10 func
free:u10 func
</symbols>
<profiles>
  active: c-framework
  c-framework:
    confidence: 0.5
    tags:
      - domain:language-tooling
      - runtime:native
      - stack:c-framework
  system-c:
    confidence: 0.4
    tags:
      - domain:system
      - lang:c
      - runtime:native
</profiles>
</pir>