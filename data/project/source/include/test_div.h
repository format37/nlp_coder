#include "init_zero.h"
#include "bn_print.h"
#include "bn_div.h"

// Test kernel for bn_divide
__global__ void test_div() {
    
    const int num_tests = 3;  // Updated number of tests
    // Initialize the word_num array
    int word_num[num_tests] = {1, 4, 2};
    BN_ULONG test_values_dividend[][MAX_BIGNUM_WORDS] = {        
        {0xB}, // 0
        {0x1,0,0,0}, // 1
        {0x7234567890ABCDEF, 0x1234567890ABCDEF} // 2
    };

    BN_ULONG test_values_divisor[][MAX_BIGNUM_WORDS] = {        
        {0x3}, // 0
        {0x2,0,0,0}, // 1
        {0x2, 0} // 2
    };
    int success = 0;
    // Initialize 'dividend' and 'divisor' with test values for each test
    for (int test = 0; test < num_tests; ++test) {
        printf("\nTest %d:\n", test);
        BIGNUM dividend, divisor, quotient, remainder;
        init_zero(&dividend, MAX_BIGNUM_WORDS);
        init_zero(&divisor, MAX_BIGNUM_WORDS);
        init_zero(&quotient, MAX_BIGNUM_WORDS);
        init_zero(&remainder, MAX_BIGNUM_WORDS);
        
        dividend.top = word_num[test];
        divisor.top = word_num[test];

        // Assign test values to 'dividend' and 'divisor', and initialize top accordingly
        for (int i = 0; i < word_num[test]; ++i) {
            dividend.d[i] = test_values_dividend[test][i];
            divisor.d[i] = test_values_divisor[test][i];
        }
        bn_print("# dividend : ", &dividend);
        bn_print("# divisor  : ", &divisor);
        
        // Test division
        success = bn_div(&quotient, &remainder, &dividend, &divisor);

        // Print results
        bn_print("# quotient : ", &quotient);
        bn_print("# remainder: ", &remainder);
    }
}