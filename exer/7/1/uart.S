
# UART寄存器地址定义
.equ UART0, 0x10000000

# UART寄存器偏移量
.equ RHR, 0      # 接收保持寄存器（读模式）
.equ THR, 0      # 发送保持寄存器（写模式）
.equ DLL, 0      # 除数锁存器低字节（写模式）
.equ IER, 1      # 中断使能寄存器（写模式）
.equ DLM, 1      # 除数锁存器高字节（写模式）
.equ FCR, 2      # FIFO控制寄存器（写模式）
.equ ISR, 2      # 中断状态寄存器（读模式）
.equ LCR, 3      # 线路控制寄存器
.equ MCR, 4      # 调制解调器控制寄存器
.equ LSR, 5      # 线路状态寄存器
.equ MSR, 6      # 调制解调器状态寄存器
.equ SPR, 7      # 便笺寄存器

# 线路状态寄存器位定义
.equ LSR_RX_READY, (1 << 0)  # 接收就绪
.equ LSR_TX_IDLE, (1 << 5)   # 发送空闲

.global uart_init
uart_init:
    # 禁用中断
    li t0, UART0
    li t1, 0x00
    sb t1, IER(t0)

    # 设置波特率
    # 先读取LCR并设置DLAB位（位7）
    lbu t1, LCR(t0)
    ori t1, t1, (1 << 7)
    sb t1, LCR(t0)

    # 设置除数锁存器
    li t1, 0x03
    sb t1, DLL(t0)
    li t1, 0x00
    sb t1, DLM(t0)

    # 设置数据格式：8位数据位，无奇偶校验，1位停止位
    li t1, (3 << 0)  # 8位数据位
    sb t1, LCR(t0)

    ret

.global uart_putc
uart_putc:
    # a0包含要发送的字符
    li t0, UART0

wait_tx:
    # 等待发送缓冲区空闲
    lbu t1, LSR(t0)
    andi t1, t1, LSR_TX_IDLE
    beqz t1, wait_tx

    # 发送字符
    sb a0, THR(t0)
    ret

.global uart_puts
uart_puts:
    # a0包含字符串地址
    beqz a0, done_puts

    # 保存a0，因为我们要修改它
    mv s0, a0

puts_loop:
    lbu t0, 0(s0)
    beqz t0, done_puts
    mv a0, t0
    call uart_putc
    # 恢复a0并递增
    addi s0, s0, 1
    j puts_loop

done_puts:
    # 恢复原始a0值（虽然在函数结束时不需要）
    mv a0, s0
    ret
