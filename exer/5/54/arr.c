#include<stdio.h>
int main()
{
    int array[2] = {0x11111111, 0xffffffff};
    int i = array[0];
    int j = array[1];
    printf("%d %d\n");
    return 0;
}