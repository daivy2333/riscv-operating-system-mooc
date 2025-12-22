CC = riscv64-unknown-elf-gcc
CFLAGS = -nostdlib -fno-builtin -g -mcmodel=medany -ffreestanding -march=rv64imac_zicsr -mabi=lp64
LDFLAGS = -T linker.ld -nostdlib -static -march=rv64imac_zicsr -mabi=lp64

all: kernel.elf

kernel.elf: start.o kernel.o uart.o
	$(CC) $(LDFLAGS) -o kernel.elf start.o kernel.o uart.o

start.o: start.S
	$(CC) $(CFLAGS) -c start.S -o start.o

kernel.o: kernel.c
	$(CC) $(CFLAGS) -c kernel.c -o kernel.o

uart.o: uart.c
	$(CC) $(CFLAGS) -c uart.c -o uart.o

clean:
	rm -f *.o kernel.elf
