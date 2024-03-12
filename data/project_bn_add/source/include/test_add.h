#include "init_zero.h"
#include "bn_print.h"
#include "bn_add.h"

// Test kernel for bn_divide
__global__ void test_add() {
    
    const int num_tests = 1;  // Updated number of tests
    // Initialize the word_num array
    int word_num[num_tests] = {1};
    BN_ULONG test_values_a[][MAX_BIGNUM_WORDS] = {        
        {0x2} // 0
    };

    BN_ULONG test_values_b[][MAX_BIGNUM_WORDS] = {        
        {0x3} // 0
    };
    // Initialize 'dividend' and 'divisor' with test values for each test
    for (int test = 0; test < num_tests; ++test) {
        printf("\nTest %d:\n", test);
        BIGNUM a, b, result;
        init_zero(&a, MAX_BIGNUM_WORDS);
        init_zero(&b, MAX_BIGNUM_WORDS);
        init_zero(&result, MAX_BIGNUM_WORDS);
        
        a.top = word_num[test];
        b.top = word_num[test];
        result.top = word_num[test];

        // Assign test values to 'a' and 'b', and initialize top accordingly
        for (int i = 0; i < word_num[test]; ++i) {
            a.d[i] = test_values_a[test][i];
            b.d[i] = test_values_b[test][i];
        }
        
        // Test addiction
        absolute_add(&result, &a, &b);

        // Print results
        bn_print("a: ", &a);
        bn_print("b: ", &b);
        bn_print("result: ", &result);
    }
    printf("-- Finished testKernel for bn_divide --\n");
}