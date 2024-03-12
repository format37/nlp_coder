#include <stdio.h>
#include <cuda_runtime.h>
#include "bignum.h"
#include "test_add.h"

int main() {
    // Launch the kernel to run the test
    test_add<<<1, 1>>>();

    // Check for any errors after running the kernel
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        printf("Error: %s\n", cudaGetErrorString(err));
        return -1;
    }

    // Wait for GPU to finish before accessing on host
    cudaDeviceSynchronize();
    return 0;
}