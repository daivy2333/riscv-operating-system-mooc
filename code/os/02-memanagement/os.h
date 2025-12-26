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

/* heap management */
typedef struct block_header {
    size_t size;          // 块大小（包括头部）
    int free;             // 空闲标志（1=空闲，0=已分配）
    struct block_header *next; // 指向下一个块
} block_header_t;

extern void *malloc(size_t size);
extern void free(void *ptr);
extern void heap_init(void);

#endif /* __OS_H__ */
