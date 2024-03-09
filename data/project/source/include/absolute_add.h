#include "find_top.h"

__device__ void absolute_add(BIGNUM *result, const BIGNUM *a, const BIGNUM *b) {
    // Determine the maximum size to iterate over
    int max_top = max(a->top, b->top);
    BN_ULONG carry = 0;

    // Initialize result
    for (int i = 0; i <= max_top; ++i) {
        result->d[i] = 0;
    }
    result->top = max_top;

    for (int i = 0; i <= max_top; ++i) {
        // Extract current words or zero if one bignum is shorter
        BN_ULONG ai = (i < a->top) ? a->d[i] : 0;
        BN_ULONG bi = (i < b->top) ? b->d[i] : 0;

        // Calculate sum and carry
        BN_ULONG sum = ai + bi + carry;

        // Store result
        result->d[i] = sum & ((1ULL << BN_ULONG_NUM_BITS) - 1); // Full sum with carry included, mask with the appropriate number of bits

        // Calculate carry, respecting the full width of BN_ULONG
        carry = (sum < ai) || (carry > 0 && sum == ai) ? 1 : 0;
    }

    // Handle carry out, expand result if necessary
    if (carry > 0) {
        if (result->top < MAX_BIGNUM_WORDS - 1) {
            result->d[result->top] = carry; // Assign carry to the new word
            result->top++;
        } else {
            // Handle error: Result BIGNUM doesn't have space for an additional word.
            // This should potentially be reported back to the caller.
        }
    }

    // Find the real top after addition (no leading zeroes)
    result->top = find_top(result, MAX_BIGNUM_WORDS);
}