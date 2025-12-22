extern void uart_init(void);
extern void uart_puts(char *s);
extern int uart_putc(char ch);
extern int uart_getc(void);

void main(void)
{
	uart_init();
	uart_puts("Hello, RVOS! Input characters will be echoed back. Press Enter to start a new line.\n");

	while (1) {
		// 获取用户输入的字符
		char ch = uart_getc();

		// 回显字符
		uart_putc(ch);

		// 如果用户按下回车键，则输出换行符
		if (ch == '\r') {
			uart_putc('\n');  // 输出换行符
		}
	}
}

// 测试qemu-system-riscv64 -machine virt -bios none -kernel kernel.elf -nographic