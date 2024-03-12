#include <stdio.h>
#include <stdint.h>
#include <string.h> // For memset
// #define BN_ULONG uint64_t
// #define BN_ULONG_NUM_BITS (sizeof(BN_ULONG) * 8)
#define WORDS 4 // Define the number of words as a constant

void c_convert_to_binary_array(BN_ULONG value[], int binary[], int words) {
    for (int word = 0; word < words; ++word) {
        for (int i = 0; i < BN_ULONG_NUM_BITS; ++i) {
            binary[word * BN_ULONG_NUM_BITS + i] = (value[word] >> (BN_ULONG_NUM_BITS - 1 - i)) & 1;
        }
    }
}

void c_convert_back_to_bn_ulong(int binary[], BN_ULONG value[], int words) {
    for (int word = 0; word < words; ++word) {
        value[word] = 0;
        for (int i = 0; i < BN_ULONG_NUM_BITS; ++i) {
            value[word] |= ((BN_ULONG)binary[word * BN_ULONG_NUM_BITS + i] << (BN_ULONG_NUM_BITS - 1 - i));
        }
    }
    printf("convert_back_to_bn_ulong value: %p words: %d\n", value, words);
}

void c_binary_division(int dividend[], int divisor[], int quotient[], int remainder[], int words) {
    int total_bits = words * BN_ULONG_NUM_BITS;
    // Init temp with zeros
    int temp[total_bits];
    memset(temp, 0, sizeof(temp));
    
    for (int i = 0; i < total_bits; ++i) {
        // Shift temp left by 1
        for (int j = 0; j < total_bits - 1; ++j) {
            temp[j] = temp[j+1];
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
        if(can_subtract) {
            quotient[i] = 1;
            for (int j = total_bits - 1; j >= 0; --j) {
                temp[j] -= divisor[j];
                if (temp[j] < 0) {  // Borrow from the next bit if needed
                    temp[j] += 2;
                    temp[j-1] -= 1;
                }
            }
        } else {
            quotient[i] = 0;
        }
    }

    // Remainder is in temp after division
    memcpy(remainder, temp, total_bits * sizeof(int));
}

void binary_mul(int a[], int b[], int result[], int words) {
    int total_bits = words * BN_ULONG_NUM_BITS;
    // Init result with zeros
    memset(result, 0, total_bits * sizeof(int));
    for (int i = 0; i < total_bits; ++i) {
        if (b[i]) {
            int carry = 0;
            for (int j = total_bits - 1; j >= 0; --j) {
                int sum = result[j] + a[j - i + total_bits - 1] + carry;
                result[j] = sum & 1;
                carry = sum >> 1;
            }
        }
    }
}

void binary_add(int a[], int b[], int result[], int words) {
    int total_bits = words * BN_ULONG_NUM_BITS;
    // Init result with zeros
    memset(result, 0, total_bits * sizeof(int));

    int carry = 0;
    for (int i = total_bits - 1; i >= 0; --i) {
        result[i] = a[i] + b[i] + carry;
        if (result[i] > 1) {
            result[i] -= 2;
            carry = 1;
        } else {
            carry = 0;
        }
    }
}

void c_bn_div_test(BN_ULONG *A, BN_ULONG *B) {
    // BN_ULONG A[WORDS] = {0, 0, 0x1, 0x0000000000000005}; // Example values for A is B
    // BN_ULONG B[WORDS] = {0, 0, 0, 0x2}; // Example values for B is 3
    //BN_ULONG A[WORDS] = {0, 0, 0, 0xB};
    //BN_ULONG B[WORDS] = {0, 0, 0, 0x3};
    //for (int test=0; test<num_tests; test++) {
        //printf("\nTest %d:\n", test);
        //BN_ULONG A[WORDS] = {test_values_dividend[test]};
        //BN_ULONG B[WORDS] = {test_values_divisor[test]};

    int binary_A[WORDS * BN_ULONG_NUM_BITS];
    int binary_B[WORDS * BN_ULONG_NUM_BITS];
    int binary_quotient[WORDS * BN_ULONG_NUM_BITS];
    int binary_remainder[WORDS * BN_ULONG_NUM_BITS];

    memset(binary_quotient, 0, sizeof(binary_quotient)); // Zero-initialize the array
    memset(binary_remainder, 0, sizeof(binary_remainder)); // Zero-initialize the array

    c_convert_to_binary_array(A, binary_A, WORDS);
    c_convert_to_binary_array(B, binary_B, WORDS);

    // Print the binary arrays
    printf("\nBinary dividend: ");
    for (int i = 0; i < WORDS * BN_ULONG_NUM_BITS; ++i) {
        printf("%d", binary_A[i]);
        if ((i + 1) % BN_ULONG_NUM_BITS == 0) {
            printf("\n");
        }
    }
    printf("\nBinary divisor: ");
    for (int i = 0; i < WORDS * BN_ULONG_NUM_BITS; ++i) {
        printf("%d", binary_B[i]);
        if ((i + 1) % BN_ULONG_NUM_BITS == 0) {
            printf("\n");
        }
    }
    printf("\n");
    
    c_binary_division(binary_A, binary_B, binary_quotient, binary_remainder, WORDS);

    // Print the binary arrays
    printf("\nBinary quotient: ");
    for (int i = 0; i < WORDS * BN_ULONG_NUM_BITS; ++i) {
        printf("%d", binary_quotient[i]);
        if ((i + 1) % BN_ULONG_NUM_BITS == 0) {
            printf("\n");
        }
    }
    printf("\nBinary remainder: ");
    for (int i = 0; i < WORDS * BN_ULONG_NUM_BITS; ++i) {
        printf("%d", binary_remainder[i]);
        if ((i + 1) % BN_ULONG_NUM_BITS == 0) {
            printf("\n");
        }
    }
    printf("\n");

    BN_ULONG quotient[WORDS];
    BN_ULONG remainder[WORDS];

    c_convert_back_to_bn_ulong(binary_quotient, quotient, WORDS);
    c_convert_back_to_bn_ulong(binary_remainder, remainder, WORDS);

    printf("A: ");
    for (int i = 0; i < WORDS; ++i) {
        printf("%016lx ", A[i]);
    }
    printf("\nB: ");
    for (int i = 0; i < WORDS; ++i) {
        printf("%016lx ", B[i]);
    }
    printf("\n# Quotient: ");
    for (int i = 0; i < WORDS; ++i) {
        printf("%016lx ", quotient[i]);
    }
    printf("\n# Remainder: ");
    for (int i = 0; i < WORDS; ++i) {
        printf("%016lx ", remainder[i]);
    }
    printf("\n");
}