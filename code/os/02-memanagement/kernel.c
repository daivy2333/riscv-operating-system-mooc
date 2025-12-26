#include "os.h"

/*
 * Following functions SHOULD be called ONLY ONE time here,
 * so just declared here ONCE and NOT included in file os.h.
 */
extern void uart_init(void);
extern void page_init(void);

void start_kernel(void)
{
	uart_init();
	uart_puts("Hello, RVOS!\n");

	page_init();

	heap_init();

	/* 测试malloc和free */
	printf("\n=== Testing malloc and free ===\n");

	void *p1 = malloc(100);
	printf("Allocated p1 = %p (size = 100)\n", p1);

	void *p2 = malloc(200);
	printf("Allocated p2 = %p (size = 200)\n", p2);

	free(p1);
	printf("Freed p1\n");

	void *p3 = malloc(50);
	printf("Allocated p3 = %p (size = 50, should reuse p1)\n", p3);

	free(p2);
	printf("Freed p2\n");

	free(p3);
	printf("Freed p3\n");

	printf("\n=== Test completed ===\n");

	while (1) {}; // stop here!
}

