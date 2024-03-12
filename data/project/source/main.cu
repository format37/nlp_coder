#include <stdio.h>
#include <cuda_runtime.h>
#include "bignum.h"
#include "test_div.h"
#include "c_test.h"

int main() {
    BN_ULONG test_values_dividend[][MAX_BIGNUM_WORDS] = {
        {0,0,0,0xB}, // 0
        {0x1,0,0,0}, // 1
        {0,0,0x1234567890ABCDEF,0x7234567890ABCDEF}, // 2
        {0x1,0,0,0} // 3
    };

    BN_ULONG test_values_divisor[][MAX_BIGNUM_WORDS] = {
        {0,0,0,0x3}, // 0
        {0x2,0,0,0}, // 1
        {0,0,0x2,0}, // 2
        {0,0,0x100,0} // 3
    };

    int num_tests = sizeof(test_values_dividend) / sizeof(test_values_dividend[0]);

    printf("\n\n### C test, expected results:\n");
    for (int i = 0; i < num_tests; i++) {
        printf("\nTest %d:\n", i);
        c_bn_div_test(test_values_dividend[i], test_values_divisor[i]);
    }

    printf("\n\n### CUDA test:\n");

    BN_ULONG *d_A, *d_B;
    cudaMalloc((void**)&d_A, MAX_BIGNUM_WORDS * sizeof(BN_ULONG));
    cudaMalloc((void**)&d_B, MAX_BIGNUM_WORDS * sizeof(BN_ULONG));

    for (int i = 0; i < num_tests; i++) {
        printf("\nTest %d:\n", i);

        cudaMemcpy(d_A, test_values_dividend[i], MAX_BIGNUM_WORDS * sizeof(BN_ULONG), cudaMemcpyHostToDevice);
        cudaMemcpy(d_B, test_values_divisor[i], MAX_BIGNUM_WORDS * sizeof(BN_ULONG), cudaMemcpyHostToDevice);

        // Launch the kernel to run the test
        test_div<<<1, 1>>>(d_A, d_B);

        // Check for any errors after running the kernel
        cudaError_t err = cudaGetLastError();
        if (err != cudaSuccess) {
            printf("Error: %s\n", cudaGetErrorString(err));
            return -1;
        }

        // Wait for GPU to finish before accessing on host
        cudaDeviceSynchronize();
    }

    cudaFree(d_A);
    cudaFree(d_B);
    return 0;
}