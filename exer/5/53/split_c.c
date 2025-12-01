#include <stdio.h>

int main() {
    unsigned int num = 0x87654321;
    unsigned int low16 = num & 0xFFFF;        // 低16位
    unsigned int high16 = (num >> 16) & 0xFFFF; // 高16位

    // 打印结果（可选，裸机环境下可能无法打印）
    printf("Low 16: 0x%04x\n", low16);
    printf("High 16: 0x%04x\n", high16);

    return 0;
}