__device__ void binary_print_big_endian(const char* msg, int binary[], int total_bits) {
    printf("\n%s: \n", msg);

    for (int i = 0; i < total_bits; i++) {
        printf("%d", binary[i]);
        if ((i + 1) % BN_ULONG_NUM_BITS == 0) {
            printf("\n");
        }
    }
    printf("\n");
}