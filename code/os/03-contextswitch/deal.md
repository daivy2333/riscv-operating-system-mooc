根据你提供的项目结构（<pir> 内容）和图片中的练习要求，你需要在一个现有的任务调度系统（sched.c 等）基础上，实现改进的任务管理功能。下面是一个清晰的实现方案和步骤。

1. 理解当前项目架构

从 <symbols> 可以看出，这是一个上下文切换/任务调度项目：

• sched.c：核心调度模块，包含 sched_init, schedule, task_delay, user_task0 等函数

• entry.S：包含 switch_to 标签，实现上下文切换的汇编代码

• kernel.c：包含 start_kernel 函数，是内核的入口点

• 其他文件是基础支持（内存、串口、打印等）

2. 核心任务：改进任务管理系统

2.1 当前状态分析

从符号表看，已有基本调度框架：
• schedule()：调度函数

• task_delay()：任务延迟

• user_task0()：示例任务

2.2 需要实现的改进

根据图片中的要求：

1. 改进 task_create() 函数

当前函数（推测）：
int task_create(void (*func)(void));


需要改进为：
int task_create(void (*func)(void *param), void *param, uint8_t priority);


改进点：
1. 参数传递：任务函数可带参数（void *param）
2. 优先级支持：256级优先级（0最高，255最低）
3. 调度算法：从简单轮转改为优先级调度

2. 增加 task_exit() 函数

void task_exit(void);


功能：任务可主动退出，内核回收资源并调度下一个任务

3. 详细实现方案

3.1 修改任务控制块（TCB）结构

首先需要在 sched.c 或 os.h 中定义/修改任务控制块：
typedef struct task_context {
    // 寄存器保存区域（用于上下文切换）
    // 根据你的架构定义，比如RISC-V需要保存ra, sp, s0-s11等
} task_context_t;

typedef struct task_control_block {
    uint32_t id;                // 任务ID
    uint8_t priority;          // 优先级（0-255，0最高）
    uint8_t state;             // 状态：RUNNING, READY, BLOCKED, EXITED
    void *stack;               // 栈指针
    task_context_t context;    // 上下文
    void (*entry)(void *);     // 任务入口函数
    void *param;               // 参数
    struct task_control_block *next;  // 就绪队列链表指针
} tcb_t;


3.2 实现改进的 task_create()

#define MAX_PRIORITY 256
#define TASK_STACK_SIZE 4096  // 每个任务的栈大小

// 就绪队列数组，每个优先级一个链表
static tcb_t *ready_queue[MAX_PRIORITY];
static uint32_t task_id_counter = 0;

int task_create(void (*func)(void *), void *param, uint8_t priority) {
    if (priority >= MAX_PRIORITY) {
        return -1;  // 优先级无效
    }
    
    // 1. 分配TCB
    tcb_t *new_task = (tcb_t *)malloc(sizeof(tcb_t));
    if (!new_task) return -1;
    
    // 2. 分配任务栈
    new_task->stack = malloc(TASK_STACK_SIZE);
    if (!new_task->stack) {
        free(new_task);
        return -1;
    }
    
    // 3. 初始化任务控制块
    new_task->id = task_id_counter++;
    new_task->priority = priority;
    new_task->state = READY;
    new_task->entry = func;
    new_task->param = param;
    new_task->next = NULL;
    
    // 4. 初始化任务上下文
    // 设置栈指针指向分配的栈顶部
    uintptr_t stack_top = (uintptr_t)new_task->stack + TASK_STACK_SIZE;
    
    // 初始化上下文，设置入口点
    // 伪代码，具体取决于架构：
    // context_init(&new_task->context, stack_top, func_wrapper);
    
    // 5. 将任务加入就绪队列
    // 按优先级插入队列
    if (!ready_queue[priority]) {
        ready_queue[priority] = new_task;
    } else {
        // 插入链表末尾
        tcb_t *p = ready_queue[priority];
        while (p->next) p = p->next;
        p->next = new_task;
    }
    
    return new_task->id;
}


任务函数包装器（用于处理参数传递）：
static void task_wrapper(void) {
    // 获取当前任务TCB
    tcb_t *current = get_current_task();
    
    // 调用真正的任务函数
    current->entry(current->param);
    
    // 任务执行完毕，退出
    task_exit();
}


3.3 实现 task_exit()

void task_exit(void) {
    tcb_t *current = get_current_task();
    
    // 1. 标记任务为退出状态
    current->state = EXITED;
    
    // 2. 从就绪队列中移除
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
    
    // 3. 可选：延迟释放资源（在调度器中释放）
    // 4. 调度下一个任务
    schedule();
    
    // 不会执行到这里
}


3.4 修改调度算法 schedule()

从简单轮转改为优先级调度：
void schedule(void) {
    tcb_t *prev = current_task;
    tcb_t *next = NULL;
    
    // 1. 从最高优先级（0）开始查找
    for (int i = 0; i < MAX_PRIORITY; i++) {
        if (ready_queue[i]) {
            // 2. 同一优先级内轮转调度
            if (!current_task || current_task->priority != i) {
                // 切换到该优先级的第一个任务
                next = ready_queue[i];
            } else {
                // 在当前优先级内轮转
                if (current_task->next) {
                    next = current_task->next;
                } else {
                    next = ready_queue[i];  // 回到队列头
                }
            }
            break;
        }
    }
    
    if (!next) {
        // 没有可运行任务，进入空闲循环
        idle_task();
        return;
    }
    
    if (prev != next) {
        // 3. 上下文切换
        switch_to(&prev->context, &next->context);
    }
}


3.5 修改汇编代码 entry.S

需要确保 switch_to 能正确保存和恢复所有必要的寄存器。对于带参数的任务，可能需要在任务初始化时设置好参数寄存器。

4. 整合步骤

步骤1：修改数据结构

1. 在 os.h 中定义新的TCB结构
2. 添加任务状态定义：READY, RUNNING, BLOCKED, EXITED

步骤2：修改现有函数

1. 更新 sched_init() 初始化优先级队列数组
2. 修改 schedule() 实现优先级调度

步骤3：实现新函数

1. 实现新版的 task_create()
2. 实现 task_exit()
3. 实现辅助函数如 get_current_task()

步骤4：测试

在 kernel.c 的 start_kernel 中测试：
void task1(void *param) {
    printf("Task 1 running with param: %p\n", param);
    while(1) {
        printf("Task 1\n");
        task_delay(1000);
    }
}

void task2(void *param) {
    printf("Task 2 running\n");
    for (int i = 0; i < 5; i++) {
        printf("Task 2 count: %d\n", i);
        task_delay(500);
    }
    task_exit();  // 任务2主动退出
}

void start_kernel(void) {
    uart_init();
    sched_init();
    
    // 创建任务，不同优先级
    task_create(task1, (void*)0x1234, 1);  // 优先级1
    task_create(task2, NULL, 0);           // 优先级0（更高）
    
    // 开始调度
    schedule();
    
    while(1) {}
}


5. 注意事项

1. 栈对齐：确保任务栈按架构要求对齐
2. 临界区保护：如果后续支持中断，需要加锁保护就绪队列
3. 空闲任务：当没有任务可运行时，应有一个空闲任务
4. 资源回收：task_exit() 后需要回收栈和TCB内存
5. 第一个任务：需要为初始的 start_kernel 创建一个TCB

6. 可能的挑战和解决方案

• 参数传递：需要在任务初始化时设置好参数寄存器的值

• 优先级反转：简单的优先级调度可能产生优先级反转问题

• 任务退出：确保退出的任务不会再次被调度

• 内存管理：需要与 page.c 的内存分配器配合

这个方案让你在现有框架上逐步添加优先级调度和任务退出功能。需要根据你的具体架构（RISC-V）调整上下文切换的细节。