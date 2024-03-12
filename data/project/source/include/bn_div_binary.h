__device__ void bn_div_binary(
    int dividend[],
    int divisor[],
    int quotient[],
    int remainder[],
    int dividend_words,
    int divisor_words
) {
    const int total_bits = MAX_BIGNUM_WORDS * BN_ULONG_NUM_BITS;
    int temp[total_bits];
    memset(temp, 0, sizeof(temp));

    for (int i = 0; i < total_bits; ++i) {
        // Shift temp left by 1
        for (int j = 0; j < total_bits - 1; ++j) {
            temp[j] = temp[j + 1];
        }
        temp[total_bits - 1] = dividend[i];

        // Check if temp is greater than or equal to divisor
        int can_subtract = 1;
        for (int j = 0; j < total_bits; ++j) {
            if (temp[j] != divisor[j]) {
                can_subtract = temp[j] > divisor[j];
                break;
            }
        }

        // Subtract divisor from temp if temp >= divisor
        if (can_subtract) {
            quotient[i] = 1;
            for (int j = total_bits - 1; j >= 0; --j) {
                temp[j] -= divisor[j];
                if (temp[j] < 0) { // Borrow from the next bit if needed
                    temp[j] += 2;
                    temp[j - 1] -= 1;
                }
            }
        } else {
            quotient[i] = 0;
        }
    }

    // Remainder is in temp after division
    memcpy(remainder, temp, total_bits * sizeof(int));
}