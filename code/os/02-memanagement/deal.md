1. 理解当前项目架构

从 <symbols> 和 <units> 可以看出，项目已经有一个基础的页式内存管理器（在 page.c 中），并包含了串口输出、启动代码等基础设施。关键文件如下：

• page.c：实现了页级内存管理函数（如 page_init, page_free, page_test 等）。

• kernel.c：包含 start_kernel 函数，是内核的入口点。

• mem.S：可能包含底层内存操作（如设置堆区域）。

• os.ld：链接脚本，定义了内存布局（包括 _heap_start 和 _heap_size 等符号）。

• types.h / os.h：头文件，定义数据类型和系统接口。

2. 核心任务：实现 malloc 和 free

你需要在页分配的基础上构建字节级分配器。这意味着：
• 使用 page_alloc（或类似函数）从操作系统获取大块内存（一页或多页）。

• 在这些页内部切割出小块内存（精确到字节）给用户程序。

• 管理这些小块内存的分配与释放，避免碎片化。

2.1 选择内存管理算法

常见的简单算法有：
• 隐式空闲链表（Implicit Free List）：在每个内存块头部存储块大小和分配状态。

• 显式空闲链表（Explicit Free List）：空闲块之间用指针连接，分配更快但更复杂。

• 分离空闲链表（Segregated Free Lists）：按大小分类的空闲链表，适合高性能。

推荐初学者使用隐式空闲链表（简单易懂，适合教学）。

2.2 步骤分解

步骤 1：定义内存块结构

在 os.h 或新建 malloc.h 中定义内存块的头部信息：
typedef struct block_header {
    size_t size;          // 块大小（包括头部）
    int free;             // 空闲标志（1=空闲，0=已分配）
    struct block_header *next; // 指向下一个块（可选）
} block_header_t;


步骤 2：初始化堆

在 kernel.c 的 start_kernel 中或单独初始化函数中：
• 使用链接脚本中定义的 _heap_start 和 _heap_size 作为堆的起始地址和大小。

• 如果没有预定义堆，则调用 page_alloc 获取一页或多页内存作为堆空间。

• 将整个堆初始化为一个大空闲块，设置好头部信息。

步骤 3：实现 malloc

void *malloc(size_t size) {
    // 1. 对齐要求（例如8字节对齐）
    size_t aligned_size = ALIGN(size + sizeof(block_header_t), 8);
    
    // 2. 遍历空闲链表，寻找第一个足够大的空闲块（首次适应算法）
    block_header_t *current = heap_start;
    while (current) {
        if (current->free && current->size >= aligned_size) {
            // 3. 如果块远大于所需，可以分割
            if (current->size > aligned_size + sizeof(block_header_t) + 8) {
                split_block(current, aligned_size);
            }
            current->free = 0;
            // 4. 返回给用户的数据区地址（跳过头部）
            return (void*)((char*)current + sizeof(block_header_t));
        }
        current = current->next;
    }
    
    // 5. 没有足够空间，扩展堆（调用page_alloc获取更多页）
    void *new_page = sbrk(PAGE_SIZE); // 或类似函数
    if (new_page == (void*)-1) return NULL;
    // 将新页添加到堆末尾，初始化空闲块，并重新尝试分配
    return malloc(size); // 递归调用
}


步骤 4：实现 free

void free(void *ptr) {
    if (!ptr) return;
    
    // 1. 获取块头部
    block_header_t *block = (block_header_t*)((char*)ptr - sizeof(block_header_t));
    
    // 2. 标记为空闲
    block->free = 1;
    
    // 3. 合并相邻空闲块（减少碎片）
    coalesce(block);
}


步骤 5：辅助函数

需要实现：
• split_block(block_header_t *block, size_t size)：分割大块。

• coalesce(block_header_t *block)：合并相邻空闲块。

• sbrk(int increment)：扩展堆空间（可用 page_alloc 实现）。

2.3 与现有代码整合

• 修改 os.h 添加 malloc/free 的函数声明。

• 在 kernel.c 中调用初始化函数。

• 确保链接脚本 (os.ld) 为堆留出足够空间。

3. 测试方案

1. 单元测试：在 kernel.c 的 start_kernel 中添加简单测试：
   void *p1 = malloc(100);
   void *p2 = malloc(200);
   free(p1);
   void *p3 = malloc(50); // 应复用p1的空间
   

2. 使用 printf 调试：利用现有的 printf.c 输出分配信息。

3. 页分配验证：确保 malloc 在需要时正确调用页分配函数。

4. 注意事项

• 线程安全：此练习可能不考虑多线程，但真实系统中需要加锁。

• 性能：首次适应算法可能产生碎片，但对练习足够。

• 边界检查：确保不超出堆边界。

• 对齐：返回的地址应满足基本对齐要求（如8字节）。

5. 参考实现顺序

1. 阅读 page.c 理解现有页分配接口。
2. 设计内存块结构体和全局堆指针。
3. 实现堆初始化和 malloc（不考虑分割和合并）。
4. 实现 free 和块合并。
5. 添加块分割优化。
6. 测试并调试。
