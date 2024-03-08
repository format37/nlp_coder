#include "bn.h"
#include <assert.h>
#define BN_ULONG_NUM_BITS 64
#define MAX_BIGNUM_WORDS 4     // For 256-bit numbers

typedef struct bignum_st {
  BN_ULONG *d;
  int top;
  int dmax;
  int neg;
  int flags;
} BIGNUM;

__device__ void bn_print(const char* msg, BIGNUM* a) {
    printf("%s", msg);
    if (a->top == 0) {
        printf("0\n");  // Handle the case where BIGNUM is zero
        return;
    }
    if (a->neg) {
        printf("-");  // Handle the case where BIGNUM is negative
    }
    for (int i = a->top - 1; i >= 0; i--) {
        // Print words up to top - 1 with appropriate formatting
        if (i == a->top - 1) {
            printf("%llx", a->d[i]);
        } else {
            printf(" %016llx", a->d[i]);
        }
    }
    printf("\n");
}

__device__ int find_top(BIGNUM *bn, int max_words) {
    for (int i = max_words - 1; i >= 0; i--) {
        if (bn->d[i] != 0) {
            return i + 1;  // The top index is the index of the last non-zero word plus one
        }
    }
    return 1; // If all words are zero, the top is 0
}

__device__ bool bn_is_zero(BIGNUM *a) {
    // Check a top
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

__device__ void init_zero(BIGNUM *bn, int capacity) {
    bn->d = new BN_ULONG[capacity]; // Dynamically allocate the required number of words.
    for (int i = 0; i < capacity; i++) {
        bn->d[i] = 0;
    }

    // top is used for representing the actual size of the 
    // significant part of the number for calculation purposes.
    bn->top = 1; // There are no significant digits when all words are zero.

    bn->neg = 0;
    
    // dmax is used to manage the memory allocation and ensure you 
    // do not access out-of-bounds memory.
    bn->dmax = capacity; // Make sure to track the capacity in dmax.
}

__device__ int bn_divide_rev3(BIGNUM *quotient, BIGNUM *remainder, BIGNUM *dividend, BIGNUM *divisor) {
    /*
    - `dv` (quotient) is where the result of the division is stored.
    - `rem` (remainder) is where the remainder of the division is stored.
    - `m` is the dividend.
    - `d` is the divisor.
    - `ctx` is the context used for memory management during the operation in original OpenSSL implementation.
    */

    // dividend
    // -------- = quotient, remainder
    // divisor
    // init zero to quotient and remainder
    init_zero(quotient, MAX_BIGNUM_WORDS);
    init_zero(remainder, MAX_BIGNUM_WORDS);
    quotient->neg = 0;
    remainder->neg = 0;
    printf("++ bn_divide_rev3 ++\n");
    bn_print(">> dividend: ", dividend);
    bn_print(">> divisor: ", divisor);
    printf("# divisor top: %d\n", divisor->top);
    bn_print(">> quotient: ", quotient);
    bn_print(">> remainder: ", remainder);    
    // Error checks similar to OpenSSL
    if (divisor == NULL || bn_is_zero(divisor)) {
        // Handle division by zero or similar error
        return 0;
    }
    if (dividend == NULL) {
        // Handle invalid dividend
        return 0;
    }

    // Implement the division algorithm here

    bn_print("\n<< quotient: ", quotient);
    printf("# bignum quotient top: %d\n", quotient->top);
    bn_print("<< remainder: ", remainder);
    printf("# bignum remainder top: %d\n", remainder->top);
    
    printf("-- bn_divide_rev3 --\n\n");

    return 1;
}