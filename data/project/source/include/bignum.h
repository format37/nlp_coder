#include "bn.h"
#include <assert.h>
// #define BN_ULONG_NUM_BITS 64
#define BN_ULONG_NUM_BITS (sizeof(BN_ULONG) * 8)
#define MAX_BIGNUM_WORDS 4     // For 256-bit numbers

typedef struct bignum_st {
  BN_ULONG *d;
  int top;
  int dmax;
  int neg;
  int flags;
} BIGNUM;