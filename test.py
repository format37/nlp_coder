from coder_tools import (
    get_file_list, 
    show_files_content,
    remove_file,
    update_file,
    cuda_compilation,
    run_program
)

"""result = update_file("[source/hello.cu]Bublo World")
print(f'result: {result}')
# print(get_file_list())
print(show_files_content("hello.*"))
# print(remove_file("source/extra.cu"))
# print(get_file_list())
result = update_file("[source/hello.cu]\nmerlo volt\n")
print(f'result: {result}')
print(show_files_content("hello.*"))"""
# Compile
result = cuda_compilation("source/main.cu")
print(f'result: {result}')
# Run program
result = run_program("")
print(f'result: {result}')