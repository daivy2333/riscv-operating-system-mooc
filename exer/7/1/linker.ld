
OUTPUT_ARCH( "riscv" )

ENTRY( start_kernel )

BASE_ADDRESS = 0x80000000;

SECTIONS
{
    . = BASE_ADDRESS;
    .text : {
        *(.text)
    }
    .rodata : {
        *(.rodata)
    }
    .data : {
        *(.data)
    }
    .bss : {
        __bss_start = .;
        *(.bss)
        *(.sbss)
        *(.scommon)
        __bss_end = .;
    }
    . = ALIGN(0x1000); /* page align */
    _end = .;
}
