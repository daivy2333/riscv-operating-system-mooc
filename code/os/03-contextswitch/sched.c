#include "os.h"

/* defined in entry.S */
extern void switch_to(struct context *next);

#define STACK_SIZE 4096
#define MAX_PRIORITY 256

/* Ready queue for each priority level */
static tcb_t *ready_queue[MAX_PRIORITY];
static tcb_t *current_task = NULL;
static uint32_t task_id_counter = 0;

static void w_mscratch(reg_t x)
{
	asm volatile("csrw mscratch, %0" : : "r" (x));
}

/* Debug function to print switch_to information */
void debug_switch_to(reg_t a0, reg_t t6, reg_t mscratch)
{
	printf("switch_to: a0=%p, t6=%p, mscratch=%p\n", (void*)a0, (void*)t6, (void*)mscratch);
}

/* Task wrapper to handle parameter passing and task exit */
static void task_wrapper(void)
{
	printf("task_wrapper: entered\n");
	tcb_t *current = current_task;
	printf("task_wrapper: current_task=%p, entry=%p, param=%p\n", 
	       current, current ? current->entry : 0, current ? current->param : 0);
	if (current && current->entry) {
		current->entry(current->param);
	}
	printf("task_wrapper: task exited\n");
	task_exit();
}

/* Get current task */
tcb_t *get_current_task(void)
{
	return current_task;
}

/* Forward declaration */
void schedule(void);

/* Initialize scheduler */
void sched_init(void)
{
	w_mscratch(0);
	
	/* Initialize ready queues */
	for (int i = 0; i < MAX_PRIORITY; i++) {
		ready_queue[i] = NULL;
	}
	
	current_task = NULL;
	task_id_counter = 0;
}

/* Create a new task */
int task_create(void (*func)(void *), void *param, uint8_t priority)
{
	printf("task_create: called with priority %d\n", priority);

	if (priority >= MAX_PRIORITY) {
		printf("task_create: invalid priority\n");
		return -1;  /* Invalid priority */
	}

	/* Allocate TCB */
	tcb_t *new_task = (tcb_t *)page_alloc(1);
	if (!new_task) {
		printf("task_create: failed to allocate TCB\n");
		return -1;
	}

	/* Allocate task stack */
	new_task->stack = page_alloc(STACK_SIZE / 4096);  /* Allocate pages for stack */
	if (!new_task->stack) {
		printf("task_create: failed to allocate stack\n");
		page_free(new_task);
		return -1;
	}

	printf("task_create: allocated TCB at %p, stack at %p\n", new_task, new_task->stack);

	/* Initialize TCB */
	new_task->id = task_id_counter++;
	new_task->priority = priority;
	new_task->state = TASK_READY;
	new_task->entry = func;
	new_task->param = param;
	new_task->next = NULL;

	/* Initialize task context */
	reg_t stack_top = (reg_t)new_task->stack + STACK_SIZE;
	/* Ensure stack is 16-byte aligned */
	stack_top = stack_top & ~0xF;
	/* Initialize all context registers to 0 */
	reg_t *ctx = (reg_t *)&new_task->context;
	for (int i = 0; i < 31; i++) {
		ctx[i] = 0;
	}
	
	/* Set up initial context */
	new_task->context.sp = stack_top;
	new_task->context.ra = (reg_t)task_wrapper;
	/* Set a0 register to hold the parameter */
	new_task->context.a0 = (reg_t)param;

	printf("task_create: context initialized\n");
	printf("task_create: sp=%p, ra=%p, a0=%p\n",
	       (void*)new_task->context.sp, (void*)new_task->context.ra, (void*)new_task->context.a0);

	/* Add task to ready queue */
	if (!ready_queue[priority]) {
		ready_queue[priority] = new_task;
	} else {
		/* Insert at the end of the queue */
		tcb_t *p = ready_queue[priority];
		while (p->next) {
			p = p->next;
		}
		p->next = new_task;
	}

	return new_task->id;
}

/* Exit current task */
void task_exit(void)
{
	tcb_t *current = current_task;
	if (!current) {
		return;
	}

	/* Mark task as exited */
	current->state = TASK_EXITED;

	/* Remove from ready queue */
	uint8_t prio = current->priority;
	tcb_t *prev = NULL;
	tcb_t *p = ready_queue[prio];

	while (p) {
		if (p == current) {
			if (prev) {
				prev->next = p->next;
			} else {
				ready_queue[prio] = p->next;
			}
			break;
		}
		prev = p;
		p = p->next;
	}

	/* Free resources */
	if (current->stack) {
		page_free(current->stack);
	}
	page_free(current);

	/* Schedule next task */
	schedule();
}

/* Schedule next task */
void schedule(void)
{
	tcb_t *next = NULL;

	printf("schedule: called\n");

	/* Find the highest priority ready task */
	for (int i = 0; i < MAX_PRIORITY; i++) {
		if (ready_queue[i]) {
			printf("schedule: found task at priority %d\n", i);
			/* Round-robin within same priority */
			if (!current_task || current_task->priority != i || current_task->state != TASK_READY) {
				next = ready_queue[i];
			} else {
				/* Move to next task in same priority queue */
				if (current_task->next) {
					next = current_task->next;
				} else {
					next = ready_queue[i];  /* Back to head */
				}
			}
			break;
		}
	}

	if (!next) {
		/* No task to run, stay idle */
		printf("schedule: no task to run\n");
		return;
	}

	printf("schedule: switching to task %d\n", next->id);

	/* Update current task state */
	if (current_task && current_task != next && current_task->state == TASK_RUNNING) {
		current_task->state = TASK_READY;
	}

	/* Switch to next task */
	current_task = next;
	current_task->state = TASK_RUNNING;

	printf("schedule: calling switch_to\n");
	switch_to(&current_task->context);
	printf("schedule: returned from switch_to\n");
}

/* Task delay - rough implementation */
void task_delay(volatile int count)
{
	count *= 50000;
	while (count--);
}

