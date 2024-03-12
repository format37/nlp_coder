#include "find_top.h"

__device__ bool bn_is_zero(BIGNUM *a) {
    int top = find_top(a, MAX_BIGNUM_WORDS);
    if (top != a->top) {
        printf("WARNING: bn_is_zero: top is not correct\n");
        printf("a->top: %d, actual top: %d\n", a->top, top);
    }
    for (int i = 0; i < a->top; ++i) {
        if (a->d[i] != 0) {
            return false;
        }
    }
    return true;
}