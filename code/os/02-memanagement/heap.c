
#include "os.h"

/*
 * Following global vars are defined in mem.S
 */
extern ptr_t HEAP_START;
extern ptr_t HEAP_SIZE;

#define PAGE_SIZE 4096

/* 全局堆指针 */
static block_header_t *heap_start = NULL;
static block_header_t *heap_end = NULL;

/* 对齐宏 */
#define ALIGN(size, alignment) (((size) + (alignment) - 1) & ~((alignment) - 1))

/*
 * 分割块：将一个大块分割成两个块
 * block: 要分割的块
 * size: 第一个块的大小
 */
static void split_block(block_header_t *block, size_t size)
{
    block_header_t *new_block;

    /* 计算新块的地址 */
    new_block = (block_header_t *)((char *)block + size);

    /* 设置新块的大小 */
    new_block->size = block->size - size;
    new_block->free = 1;
    new_block->next = block->next;

    /* 修改原块的大小和next指针 */
    block->size = size;
    block->next = new_block;
}

/*
 * 合并相邻的空闲块
 * block: 要合并的块
 */
static void coalesce(block_header_t *block)
{
    block_header_t *prev = NULL;
    block_header_t *current = heap_start;

    /* 找到block的前一个块 */
    while (current && current != block) {
        prev = current;
        current = current->next;
    }

    /* 合并下一个块 */
    if (block->next && block->next->free) {
        block->size += block->next->size;
        block->next = block->next->next;
    }

    /* 合并前一个块 */
    if (prev && prev->free) {
        prev->size += block->size;
        prev->next = block->next;
    }
}

/*
 * 扩展堆：分配新页并添加到堆的末尾
 * size: 需要扩展的大小
 */
static void *extend_heap(size_t size)
{
    block_header_t *new_block;
    int npages;
    void *page;

    /* 计算需要分配的页数 */
    npages = (size + PAGE_SIZE - 1) / PAGE_SIZE;

    /* 分配新页 */
    page = page_alloc(npages);
    if (!page) {
        return NULL;
    }

    /* 初始化新块 */
    new_block = (block_header_t *)page;
    new_block->size = npages * PAGE_SIZE;
    new_block->free = 1;
    new_block->next = NULL;

    /* 将新块添加到堆的末尾 */
    if (heap_end) {
        heap_end->next = new_block;
    }
    heap_end = new_block;

    /* 如果堆为空，设置堆的开始 */
    if (!heap_start) {
        heap_start = new_block;
    }

    return new_block;
}

/*
 * 初始化堆
 */
void heap_init(void)
{
    /* 初始化时先不分配任何页，等到第一次malloc时再分配 */
    heap_start = NULL;
    heap_end = NULL;
}

/*
 * 分配内存
 * size: 需要分配的字节数
 * 返回: 分配的内存指针，失败返回NULL
 */
void *malloc(size_t size)
{
    block_header_t *current;
    size_t aligned_size;

    /* 对齐大小（8字节对齐）并加上头部大小 */
    aligned_size = ALIGN(size + sizeof(block_header_t), 8);

    /* 遍历空闲链表，寻找第一个足够大的空闲块（首次适应算法） */
    current = heap_start;
    while (current) {
        if (current->free && current->size >= aligned_size) {
            /* 如果块远大于所需，可以分割 */
            if (current->size > aligned_size + sizeof(block_header_t) + 8) {
                split_block(current, aligned_size);
            }
            current->free = 0;
            /* 返回给用户的数据区地址（跳过头部） */
            return (void *)((char *)current + sizeof(block_header_t));
        }
        current = current->next;
    }

    /* 没有足够空间，扩展堆 */
    current = extend_heap(aligned_size);
    if (!current) {
        return NULL;
    }

    /* 如果扩展后的块远大于所需，可以分割 */
    if (current->size > aligned_size + sizeof(block_header_t) + 8) {
        split_block(current, aligned_size);
    }
    current->free = 0;

    /* 返回给用户的数据区地址（跳过头部） */
    return (void *)((char *)current + sizeof(block_header_t));
}

/*
 * 释放内存
 * ptr: 要释放的内存指针
 */
void free(void *ptr)
{
    block_header_t *block;

    if (!ptr) {
        return;
    }

    /* 获取块头部 */
    block = (block_header_t *)((char *)ptr - sizeof(block_header_t));

    /* 标记为空闲 */
    block->free = 1;

    /* 合并相邻空闲块（减少碎片） */
    coalesce(block);
}
