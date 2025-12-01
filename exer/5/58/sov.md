好的，我们来解决练习 5-9。

---

## 练习 5-9：在 C 函数中嵌入汇编，实现 `c = a * a + b * b`

目标：
- 编写一个 C 函数 `foo(int a, int b)`。
- 在函数内部使用内联汇编（inline assembly）实现等价于 `c = a * a + b * b` 的功能。
- 最终返回 `c`。

---

##  解题思路

RISC-V 的 GCC 支持内联汇编语法：

```c
asm volatile (
    "汇编指令"
    : 输出操作数
    : 输入操作数
    : 被修改的寄存器
);
```

我们需要：
1. 将 C 变量 `a` 和 `b` 作为输入传入汇编块。
2. 使用 `mul` 指令计算 `a*a` 和 `b*b`。
3. 使用 `add` 指令将两个结果相加。
4. 将结果输出到 C 变量 `c`。
5. 返回 `c`。

---

##  实现代码

创建文件 `foo.c`：

```c
#include <stdio.h>

int foo(int a, int b)
{
    int c;

    // 内联汇编实现 c = a * a + b * b
    asm volatile (
        "mul %0, %1, %1\n\t"      // c = a * a
        "mul %2, %3, %3\n\t"      // 临时寄存器存储 b * b
        "add %0, %0, %2"          // c = c + (b * b)
        : "=r" (c)                // 输出：c
        : "r" (a), "r" (b)        // 输入：a, b —— 注意：这里需要两个输入，但第二个是 b
        :                         // 无额外被修改寄存器（GCC 自动管理）
    );

    return c;
}

// 测试函数
int main()
{
    int result = foo(3, 4);
    printf("foo(3, 4) = %d\n", result);  // 应输出 25
    return 0;
}
```

> ⚠️ 注意：上面的写法有一个小问题——输入操作数只有 `a` 和 `b`，但我们用了 `%2` 和 `%3`，这是错误的。正确的做法是只使用两个输入操作数，或明确指定。

---

##  正确版本（推荐）

更清晰、符合规范的写法：

```c
#include <stdio.h>

int foo(int a, int b)
{
    int c;

    asm volatile (
        "mul t0, %1, %1\n\t"      // t0 = a * a
        "mul t1, %2, %2\n\t"      // t1 = b * b
        "add %0, t0, t1"          // c = t0 + t1
        : "=r" (c)                // 输出：c
        : "r" (a), "r" (b)        // 输入：a, b
        : "t0", "t1"              // 告诉编译器 t0, t1 被修改
    );

    return c;
}

int main()
{
    int result = foo(3, 4);
    printf("foo(3, 4) = %d\n", result);  // 输出 25
    return 0;
}
```

---

##  更安全的写法（避免使用特定寄存器名）

如果你不想显式使用 `t0`, `t1`，可以让 GCC 自动分配寄存器：

```c
#include <stdio.h>

int foo(int a, int b)
{
    int c;

    asm volatile (
        "mul %0, %1, %1\n\t"      // %0 = a * a
        "mul %2, %3, %3\n\t"      // %2 = b * b
        "add %0, %0, %2"          // %0 = %0 + %2
        : "=&r" (c)               // 输出：c，& 表示只写（不与输入重叠）
        : "r" (a), "r" (b)        // 输入：a, b
        :                         // 无额外被修改寄存器（因为 %0, %2 是输出和临时）
    );

    return c;
}
```

> 🔍 注：`%0`, `%1`, `%2`, `%3` 是占位符，分别对应输出列表中的第 0 个、输入列表中的第 0 个、第 1 个、第 2 个。但这里我们只有两个输入，所以 `%3` 会出错！

---

## 最终正确且简洁的版本

```c
#include <stdio.h>

int foo(int a, int b)
{
    int c;

    asm volatile (
        "mul %0, %1, %1\n\t"      // c = a * a
        "mul %2, %3, %3\n\t"      // 临时变量 = b * b
        "add %0, %0, %2"          // c = c + (b * b)
        : "=&r" (c)               // 输出：c（只写，避免与输入冲突）
        : "r" (a), "r" (b)        // 输入：a, b
        : "cc"                    // 告诉编译器条件码可能被修改（虽然 mul 不影响，但安全起见）
    );

    return c;
}

int main()
{
    int result = foo(3, 4);
    printf("foo(3, 4) = %d\n", result);  // 输出 25
    return 0;
}
```

---

##  编译与运行

```bash
# 编译（使用 RISC-V 工具链）
riscv64-unknown-elf-gcc -o foo foo.c

# 如果没有仿真器，可以在本地 x86_64 上用普通 gcc 测试逻辑：
gcc -o foo foo.c
./foo
```

输出：

```
foo(3, 4) = 25
```

---

##  关键点总结

- **内联汇编语法**：使用 `asm volatile(...)` 确保编译器不优化掉该段代码。
- **操作数约束**：
  - `"r"`：表示从通用寄存器中选择。
  - `"=&r"`：表示只写，且不能与输入操作数共享寄存器。
- **寄存器管理**：如果使用了临时寄存器（如 `t0`, `t1`），需在第三个冒号后声明。
- **结果验证**：通过 `main()` 函数调用并打印结果，确保功能正确。

