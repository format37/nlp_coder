__device__ void bn_print_quotient(const char* msg, BIGNUM* a) {
    printf("%s", msg);
    if (a->top == 0) {
        printf("0\n");
        return;
    }
    if (a->neg) {
        printf("-");
    }
    int i = a->top - 1;
    printf("%llx", a->d[i]);
    for (i = a->top - 2; i >= 0; i--) {
        printf("%016llx", a->d[i]);
    }
    printf("\n");
}