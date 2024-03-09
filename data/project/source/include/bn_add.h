#include "absolute_add.h"
#include "absolute_compare.h"
#include "absolute_subtract.h"

__device__ void bn_add(BIGNUM *result, BIGNUM *a, BIGNUM *b) {
    // Clear the result first.
    result->top = 0;
    for (int i = 0; i < MAX_BIGNUM_WORDS; i++) {
        result->d[i] = 0;
    }

    if (a->neg == b->neg) {
        // Both numbers have the same sign, so we can directly add them.
        absolute_add(result, a, b);
        result->neg = a->neg; // The sign will be the same as both operands.
    } else {
        // The numbers have different signs, so we need to compare their absolute values to decide on the operation.
        int cmp_result = absolute_compare(a, b);
        if (cmp_result < 0) {
            // |b| is greater than |a|, so we'll do b - a and assign the sign of b to the result.
            absolute_subtract(result, b, a);
            result->neg = b->neg;
        } else if (cmp_result > 0) {
            // |a| is greater than |b|, so we'll do a - b and assign the sign of a to the result.
            absolute_subtract(result, a, b);
            result->neg = a->neg;
        } else {
            // |a| is equal to |b|, so the result is 0.
            // The result of adding two numbers with different signs but equal magnitude is 0.
            result->neg = 0; // Set sign to 0 for non-negative.
            result->top = 1; // The result is 0, so top is 1 to denote one valid word which is zero.
            result->d[0] = 0;
        }
    }

    // Lastly, normalize the result to remove any leading zeros that could have appeared.
    find_top(result, MAX_BIGNUM_WORDS);
}