#include <stdio.h>

int foo(int a, int b)
{
    int c;

    asm volatile (
        "mul %0, %1, %1\n\t"      // c = a * a
        "mul %2, %2, %2\n\t"      // 临时变量 = b * b
        "add %0, %0, %2"          // c = c + (b * b)
        : "=&r" (c)               // 输出：c（只写，避免与输入冲突）
        : "r" (a), "r" (b)        // 输入：a, b
        : "cc"                    // 告诉编译器条件码可能被修改
    );

    return c;
}

int main()
{
    int result = foo(3, 4);
    printf("foo(3, 4) = %d\n", result);  // 输出 25
    return 0;
}
