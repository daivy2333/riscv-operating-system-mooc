#include <stdio.h>
int main()
{
    register int a,b,c,d,e;
    b = 1;
    c = 2;
    e = 3;
    a = b + c;
    d = a - e;
    printf("%d %d\n",a,b);
    return 0;
}