from coder_tools import (
    get_file_list, 
    show_files_content,
    remove_file,
    update_file,
    cuda_compilation,
    run_program
)

# result = update_file("[source/hello.cu]Bublo World")
# print(f'result: {result}')
# print(get_file_list())
# print(show_files_content("*"))
# print(remove_file("source/extra.cu"))
# print(get_file_list())
update_content = '''<<<source/include/test_add.h>>>#include \"init_zero.h\"
#include \"bn_print.h\"
#include \"bn_add.h\"

// Test kernel for bn_add
__global__ void test_add() {
    
    const int num_tests = 4;  // Updated number of tests
    // Initialize the word_num array
    int word_num[num_tests] = {1, 2, 2, 2};
    BN_ULONG test_values_a[][MAX_BIGNUM_WORDS] = {        
        {0x2}, // 2
        {0xFFFFFFFFFFFFFFFF, 0x1}, // -1
        {0x0123456789ABCDEF, 0x0}, // 0123456789ABCDEF
        {0x8000000000000000, 0x0}  // -9223372036854775808
    };

    BN_ULONG test_values_b[][MAX_BIGNUM_WORDS] = {        
        {0x3}, // 3
        {0xFFFFFFFFFFFFFFFF, 0x1}, // -1
        {0xFEDCBA9876543210, 0x0}, // FEDCBA9876543210
        {0x8000000000000000, 0x0}  // -9223372036854775808
    };
    // Initialize 'a', 'b', and 'result' with test values for each test
    for (int test = 0; test < num_tests; ++test) {
        printf(\"\\nTest %d:\\n\", test);
        BIGNUM a, b, result;
        init_zero(&a, MAX_BIGNUM_WORDS);
        init_zero(&b, MAX_BIGNUM_WORDS);
        init_zero(&result, MAX_BIGNUM_WORDS);
        
        a.top = word_num[test];
        b.top = word_num[test];
        
        // Assign test values to 'a' and 'b'
        for (int i = 0; i < word_num[test]; ++i) {
            a.d[i] = test_values_a[test][i];
            b.d[i] = test_values_b[test][i];
        }
        
        a.neg = test_values_a[test][1] != 0 ? 1 : 0;
        b.neg = test_values_b[test][1] != 0 ? 1 : 0;
        
        // Test addition
        bn_add(&result, &a, &b);

        // Print results
        bn_print(\"a: \", &a);
        bn_print(\"b: \", &b);
        bn_print(\"result: \", &result);
    }
    printf(\"-- Finished test for bn_add --\\n\");
}'''

# result = update_file(update_content)
# print(f'result: {result}')
# print(show_files_content("hello.*"))"""
# Compile
result = cuda_compilation("")
print(f'result: {result}')
# Run program
result = run_program("")
print(f'result: {result}')