// Helper function to determine the 'top' field value for a BIGNUM from a binary array
__device__ int get_bn_top_from_binary_array(const int binary[], int total_bits) {
    for (int i = total_bits - 1; i >= 0; --i) {
        if (binary[i]) {
            return (i / BN_ULONG_NUM_BITS) + 1;
        }
    }
    return 1; // If every bit is zero, top is one
}