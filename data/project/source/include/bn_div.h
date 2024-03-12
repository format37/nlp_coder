#include "bn_is_zero.h"
#include "bn_div_binary.h"
#include "bn_print_quotient.h"
#include "convert_to_binary_array.h"
#include "binary_print_big_endian.h"
#include "convert_back_to_bn_ulong.h"
#include "get_bn_top_from_binary_array.h"


__device__ int bn_div(BIGNUM *quotient, BIGNUM *remainder, BIGNUM *dividend, BIGNUM *divisor) {
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
    /*bn_print(">> dividend: ", dividend);
    bn_print(">> divisor: ", divisor);
    printf("# divisor top: %d\n", divisor->top);
    bn_print(">> quotient: ", quotient);
    bn_print(">> remainder: ", remainder);*/
    // Error checks similar to OpenSSL
    if (divisor == NULL || bn_is_zero(divisor)) {
        // Handle division by zero or similar error
        return 0;
    }
    if (dividend == NULL) {
        // Handle invalid dividend
        return 0;
    }

    const int total_bits = MAX_BIGNUM_WORDS * BN_ULONG_NUM_BITS;
    // printf("# total_bits: %d\n", total_bits);
    
    // Define arrays with the maximum size based on MAX_BIGNUM_WORDS
    int binary_dividend[total_bits] = {0};
    int binary_divisor[total_bits] = {0};
    int binary_quotient[total_bits] = {0};
    int binary_remainder[total_bits] = {0};
    
    // Initialize binary arrays
    memset(binary_quotient, 0, total_bits * sizeof(int));
    memset(binary_remainder, 0, total_bits * sizeof(int));
    
    // Convert the BIGNUMs to binary arrays, use actual 'top' value for correct size
    convert_to_binary_array(dividend->d, binary_dividend, MAX_BIGNUM_WORDS);
    convert_to_binary_array(divisor->d, binary_divisor, MAX_BIGNUM_WORDS);

    binary_print_big_endian(">> binary_dividend", binary_dividend, total_bits);
    binary_print_big_endian(">> binary_divisor", binary_divisor, total_bits);

    // Call the binary division function
    // bn_div_binary(binary_dividend, binary_divisor, binary_quotient, binary_remainder);
    // Call the binary division function with the actual number of bits used
    bn_div_binary(
        binary_dividend, 
        binary_divisor, 
        binary_quotient, 
        binary_remainder, 
        dividend->top, 
        divisor->top
        );

    //bn_print_quotient("<< binary_quotient", quotient);
    binary_print_big_endian("<< binary_quotient", binary_quotient, total_bits);
    binary_print_big_endian("<< binary_remainder", binary_remainder, total_bits);

    // Fix the 'top' fields of quotient and remainder
    quotient->top = get_bn_top_from_binary_array(binary_quotient, total_bits);
    //quotient->top = get_bn_top_from_binary_array_little_endian(binary_quotient, total_bits);
    // printf("\n# binary quotient top: %d\n", quotient->top);
    remainder->top = get_bn_top_from_binary_array(binary_remainder, total_bits);
    // printf("\n# binary remainder top: %d\n", remainder->top);

    // Convert the binary arrays back to BIGNUMs
    convert_back_to_bn_ulong(binary_quotient, quotient->d, quotient->top);
    convert_back_to_bn_ulong(binary_remainder, remainder->d, remainder->top);

    bn_print("\n<< quotient: ", quotient);
    //printf("# bignum quotient top: %d\n", quotient->top);
    bn_print("<< remainder: ", remainder);
    //printf("# bignum remainder top: %d\n", remainder->top);

    // Determine sign of quotient and remainder
    quotient->neg = dividend->neg ^ divisor->neg;
    remainder->neg = dividend->neg;

    // Update tops using find_top
    quotient->top = find_top(quotient, MAX_BIGNUM_WORDS);
    remainder->top = find_top(remainder, MAX_BIGNUM_WORDS);

    

    return 1;
}