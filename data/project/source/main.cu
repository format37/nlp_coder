#include <stdio.h>
#include <cuda_runtime.h>
#include "bignum.h"
#include "test_div.h"
#include "c_test.h"

int main() {
    
    BN_ULONG test_values_dividend[][MAX_BIGNUM_WORDS] = {        
        {0,0,0,0xB}, // 0
        {0x1,0,0,0}, // 1
        {0,0,0x1234567890ABCDEF,0x7234567890ABCDEF} // 2
    };

    BN_ULONG test_values_divisor[][MAX_BIGNUM_WORDS] = {        
        {0,0,0,0x3}, // 0
        {0x2,0,0,0}, // 1
        {0,0,0x2,0} // 2
    };

    int num_tests = sizeof(test_values_dividend) / sizeof(test_values_dividend[0]);

    //BN_ULONG A[WORDS] = {0, 0, 0, 0xB};
    //BN_ULONG B[WORDS] = {0, 0, 0, 0x3};
    printf("\n\n### C test, expected results:\n");
    for (int i = 0; i < num_tests; i++) {
        printf("Test %d:\n", i);
        c_bn_div_test(test_values_dividend[i], test_values_divisor[i]);
    }
    // c_bn_div_test(test_values_dividend, test_values_divisor, num_tests);

    /*printf("\n\n### CUDA test:\n");
    // Launch the kernel to run the test
    test_div<<<1, 1>>>();

    // Check for any errors after running the kernel
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        printf("Error: %s\n", cudaGetErrorString(err));
        return -1;
    }

    // Wait for GPU to finish before accessing on host
    cudaDeviceSynchronize();*/
    return 0;
}