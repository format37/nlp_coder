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