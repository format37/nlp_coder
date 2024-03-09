__device__ int find_top(BIGNUM *bn, int max_words) {
    for (int i = max_words - 1; i >= 0; i--) {
        if (bn->d[i] != 0) {
            return i + 1;  // The top index is the index of the last non-zero word plus one
        }
    }
    return 1; // If all words are zero, the top is 0
}