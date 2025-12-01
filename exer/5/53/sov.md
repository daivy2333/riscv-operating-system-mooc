daivy@daivy:~/projects/riscv-operating-system-mooc/exer/5/53$ riscv64-unknown-elf-gcc -o 
split_c split_c.c
daivy@daivy:~/projects/riscv-operating-system-mooc/exer/5/53$ ./split_c
Low 16: 0x4321
High 16: 0x8765
daivy@daivy:~/projects/riscv-operating-system-mooc/exer/5/53$ qemu-riscv64 split_c
Low 16: 0x4321
High 16: 0x8765
daivy@daivy:~/projects/riscv-operating-system-mooc/exer/5/53$ gcc -o a split_c.c
daivy@daivy:~/projects/riscv-operating-system-mooc/exer/5/53$ readelf -h a
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              DYN (Position-Independent Executable file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x1060
  Start of program headers:          64 (bytes into file)
  Start of section headers:          13984 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         13
  Size of section headers:           64 (bytes)
  Number of section headers:         31
  Section header string table index: 30
daivy@daivy:~/projects/riscv-operating-system-mooc/exer/5/53$ qemu-riscv64 a
qemu-riscv64: a: Invalid ELF image for this architecture

这就是a.o为什么会在这里


Breakpoint 1, 0x00000000000100b4 in _start ()
(gdb) stepi
0x00000000000100b8 in _start ()
(gdb) info registers x10 x12 x13
x10            0x21d95             138645
x12            0x0                 0
x13            0x0                 0
(gdb) stepi
0x00000000000100ba in _start ()
(gdb) info registers x10 x12 x13
x10            0x87654000          2271559680
x12            0x0                 0
x13            0x0                 0
(gdb) stepi
0x00000000000100be in _start ()
(gdb) info registers x10 x12 x13
x10            0x87654321          2271560481
x12            0x0                 0
x13            0x0                 0
(gdb) stepi
0x00000000000100c2 in _start ()
(gdb) info registers x10 x12 x13
x10            0xffffffff87654000  -2023407616
x12            0x0                 0
x13            0x0                 0
(gdb) stepi
0x00000000000100c6 in _start ()
(gdb) info registers x10 x12 x13
x10            0xffffffff87654321  -2023406815
x12            0x0                 0
x13            0x0                 0
(gdb) stepi
0x00000000000100c8 in _start ()
(gdb) info registers x10 x12 x13
x10            0xffffffff87654321  -2023406815
x12            0x0                 0
x13            0x0                 0
(gdb) stepi
0x00000000000100ca in _start ()
(gdb) info registers x10 x12 x13
x10            0xffffffff87654321  -2023406815
x12            0x0                 0
x13            0x0                 0
(gdb) stepi
0x00000000000100ce in _start ()
(gdb) info registers x10 x12 x13
x10            0xffffffff87654321  -2023406815
x12            0x4321              17185
x13            0x0                 0
(gdb) stepi
0x00000000000100d2 in _start ()
(gdb) info registers x10 x12 x13
x10            0xffffffff87654321  -2023406815
x12            0x4321              17185
x13            0xffffffff8765      281474976679781
(gdb) stepi
0x00000000000100d4 in _start ()
(gdb) info registers x10 x12 x13
x10            0xffffffff87654321  -2023406815
x12            0x4321              17185
x13            0x8765              34661

效果是这样的

