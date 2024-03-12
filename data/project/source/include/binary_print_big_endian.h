__device__ void binary_print_big_endian(const char* msg, int binary[], int total_bits) {
    printf("\n%s: \n", msg);

    // Calculate the number of full words and any additional bits in the last word
    int full_words = total_bits / BN_ULONG_NUM_BITS;
    int additional_bits = total_bits % BN_ULONG_NUM_BITS;

    // Print any additional bits in the last word first
    if (additional_bits > 0) {
        for (int i = 0; i < additional_bits; i++) {
            printf("%d", binary[i]);
        }
        printf("\n");
    }

    // Iterate through the full words in reverse order
    for (int word = full_words - 1; word >= 0; word--) {
        // Big endian
        for (int bit = BN_ULONG_NUM_BITS - 1; bit >= 0; bit--) {
            // Calculate the bit position in the binary array
            int bit_pos = word * BN_ULONG_NUM_BITS + bit;
            printf("%d", binary[bit_pos]);
        }
        // Separate 64-bit words with a space
        if (word > 0) {
            printf("\n");
        }
    }

    // New line at the end of the binary representation
    printf("\n");
}