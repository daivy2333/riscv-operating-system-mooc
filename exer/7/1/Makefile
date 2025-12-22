
CC = riscv64-unknown-elf-gcc
CFLAGS = -nostdlib -fno-builtin -g -mcmodel=medany -ffreestanding -march=rv64imac -mabi=lp64
LDFLAGS = -T linker.ld -nostdlib -static -march=rv64imac -mabi=lp64

all: kernel.elf

kernel.elf: kernel.o uart.o
	$(CC) $(LDFLAGS) -o kernel.elf kernel.o uart.o

kernel.o: kernel.S
	$(CC) $(CFLAGS) -c kernel.S -o kernel.o

uart.o: uart.S
	$(CC) $(CFLAGS) -c uart.S -o uart.o

clean:
	rm -f *.o kernel.elf
