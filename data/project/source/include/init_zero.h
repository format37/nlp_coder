__device__ void init_zero(BIGNUM *bn, int capacity) {
    bn->d = new BN_ULONG[capacity]; // Dynamically allocate the required number of words.
    for (int i = 0; i < capacity; i++) {
        bn->d[i] = 0;
    }

    // top is used for representing the actual size of the 
    // significant part of the number for calculation purposes.
    bn->top = 1; // There are no significant digits when all words are zero.

    bn->neg = 0;
    
    // dmax is used to manage the memory allocation and ensure you 
    // do not access out-of-bounds memory.
    bn->dmax = capacity; // Make sure to track the capacity in dmax.
}