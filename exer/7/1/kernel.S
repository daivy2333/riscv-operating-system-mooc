
.global start_kernel

start_kernel:
    # 调用uart_init初始化UART
    call uart_init

    # 准备"Hello, RVOS!\n"字符串
    la a0, hello_str
    call uart_puts

    # 进入无限循环
loop:
    j loop

hello_str:
    .string "Hello, RVOS!\n"
