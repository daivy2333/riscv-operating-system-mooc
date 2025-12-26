#ifndef __OS_H__
#define __OS_H__

#include "types.h"
#include "platform.h"

#include <stddef.h>
#include <stdarg.h>

/* uart */
extern int uart_putc(char ch);
extern void uart_puts(char *s);

/* printf */
extern int  printf(const char* s, ...);
extern void panic(char *s);

/* memory management */
extern void *page_alloc(int npages);
extern void page_free(void *p);

/* task management */
struct context {
	/* ignore x0 */
	reg_t ra;   /* offset 0 */
	reg_t sp;   /* offset 1 */
	/* gp and tp are not saved/restored */
	reg_t t0;   /* offset 2 */
	reg_t t1;   /* offset 3 */
	reg_t t2;   /* offset 4 */
	reg_t s0;   /* offset 5 */
	reg_t s1;   /* offset 6 */
	reg_t a0;   /* offset 7 */
	reg_t a1;   /* offset 8 */
	reg_t a2;   /* offset 9 */
	reg_t a3;   /* offset 10 */
	reg_t a4;   /* offset 11 */
	reg_t a5;   /* offset 12 */
	reg_t a6;   /* offset 13 */
	reg_t a7;   /* offset 14 */
	reg_t s2;   /* offset 15 */
	reg_t s3;   /* offset 16 */
	reg_t s4;   /* offset 17 */
	reg_t s5;   /* offset 18 */
	reg_t s6;   /* offset 19 */
	reg_t s7;   /* offset 20 */
	reg_t s8;   /* offset 21 */
	reg_t s9;   /* offset 22 */
	reg_t s10;  /* offset 23 */
	reg_t s11;  /* offset 24 */
	reg_t t3;   /* offset 25 */
	reg_t t4;   /* offset 26 */
	reg_t t5;   /* offset 27 */
	reg_t t6;   /* offset 28 */
};

/* Task states */
#define TASK_READY    0
#define TASK_RUNNING  1
#define TASK_BLOCKED  2
#define TASK_EXITED   3

/* Task Control Block */
struct task_control_block {
	uint32_t id;                /* Task ID */
	uint8_t priority;          /* Priority (0-255, 0 is highest) */
	uint8_t state;             /* Task state */
	void *stack;               /* Stack pointer */
	struct context context;    /* Context for context switch */
	void (*entry)(void *);     /* Task entry function */
	void *param;               /* Parameter for task entry */
	struct task_control_block *next;  /* Next task in ready queue */
};

typedef struct task_control_block tcb_t;

/* Task management functions */
extern tcb_t *get_current_task(void);
extern int task_create(void (*func)(void *), void *param, uint8_t priority);
extern void task_exit(void);
extern void task_delay(volatile int count);

#endif /* __OS_H__ */
