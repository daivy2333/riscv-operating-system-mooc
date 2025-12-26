#include "os.h"

/*
 * Following functions SHOULD be called ONLY ONE time here,
 * so just declared here ONCE and NOT included in file os.h.
 */
extern void uart_init(void);
extern void page_init(void);
extern void sched_init(void);
extern void schedule(void);

/* Test task 1 - higher priority */
void task1(void *param)
{
	printf("Task 1: Created with param: %p\n", param);
	while (1) {
		printf("Task 1: Running...\n");
		task_delay(1000);
	}
}

/* Test task 2 - lower priority, will exit after some iterations */
void task2(void *param)
{
	printf("Task 2: Created\n");
	for (int i = 0; i < 5; i++) {
		printf("Task 2 count: %d\n", i);
		task_delay(500);
	}
	printf("Task 2: Exiting...\n");
	task_exit();
}

/* Idle task - runs when no other task is ready */
void idle_task(void *param)
{
	printf("Idle task: Running...\n");
	while (1) {
		/* Do nothing, just wait */
	}
}

void start_kernel(void)
{
	uart_init();
	uart_puts("Hello, RVOS!\n");

	page_init();

	sched_init();

	/* Create idle task with lowest priority */
	task_create(idle_task, NULL, 255);

	/* Create tasks with different priorities */
	task_create(task1, (void*)0x1234, 1);  /* Priority 1 */
	task_create(task2, NULL, 0);           /* Priority 0 (higher) */

	printf("Starting scheduler...\n");

	/* Start scheduling - this will never return */
	schedule();

	/* Should never reach here */
	uart_puts("Would not go here!\n");
	while (1) {}; // stop here!
}

