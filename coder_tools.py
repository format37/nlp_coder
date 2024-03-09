import os
import fnmatch
from pydantic import BaseModel, Field
from typing import Optional
# import re
import subprocess


class get_file_list_args(BaseModel):
    param: str = Field(description="""Provide empty string. There is no input required.""")

def get_file_list(param=None):
# def get_file_list():
    """
    This function reads the ./data/project directory and returns a list of directories and files.
    Directories have '/' sign at the end of their names.
    Example:
    [
        "source/",
        "source/main.cu",
        "source/bignum.h",
        "source/compilation.log",
        "output/",
        "output/program.c"
    ]
    It recursively iterates through the directory and lists all files and included folders.
    The list of folders is not predefined. It is generated dynamically.
    """
    project_dir = "./data/project"
    file_list = []

    for root, dirs, files in os.walk(project_dir):
        for directory in dirs:
            relative_path = os.path.relpath(os.path.join(root, directory), project_dir)
            file_list.append(relative_path + "/")

        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), project_dir)
            file_list.append(relative_path)

    sorted_list = sorted(file_list)
    # Represent as a string with newlines
    newlines = "\n".join(sorted_list)
    return newlines


class show_files_content_args(BaseModel):
    mask: str = Field(description="""Mask that filters the files. Use * to show all files.""")

def show_files_content(mask):
    """
    This function reads each file in the ./data/project directory and returns the content of the files.
    The mask is a string that contains a list of files to be read. * will show all files.
    Each file starts with \n<<<full_file_path>>>\n and then the content of the file.
    """
    project_dir = "./data/project"
    # Remove f'{project_dir}/out/program' if exists
    program_path = f'{project_dir}/out/program'
    if os.path.exists(program_path):
        os.remove(program_path)
    file_list = get_file_list().split("\n")  # Get the list of files from get_file_list()
    file_content = ""
    for file_path in file_list:
        if file_path.endswith("/"):
            continue  # Skip directories
        file_name = os.path.basename(file_path)
        if mask == "*" or fnmatch.fnmatch(file_name, mask):
            file_content += f"\n<<<{file_path}>>>\n"
            file_full_path = os.path.join(project_dir, file_path)
            try:
                with open(file_full_path, "r", encoding="latin-1") as file:
                    content = file.read()
                    file_content += content + "\n"
            except IOError:
                file_content += "Error: Unable to read the file.\n"
    return file_content





class remove_file_args(BaseModel):
    path: str = Field(description="""Path to the file to be removed.""")

def remove_file(file_path):
    """
    This function removes a file from the ./data/project directory.
    """
    project_dir = "./data/project"
    file_full_path = os.path.join(project_dir, file_path)
    try:
        os.remove(file_full_path)
        return f"File removed: {file_path}"
    except FileNotFoundError:
        return f"Error: File not found: {file_path}"


class update_file_args(BaseModel):
    # file_path: str = Field(description="""Path to the file to be updated.""")
    # content: str = Field(description="""Content to be written to the file.""")
    file_path_and_content: str = Field(description="""Path to the file to be updated and content to be written to the file. For example, <<<file_path>>>content""")

def update_file(file_path_and_content):
    """
    This function updates a file in the ./data/project directory.
    """
    # find first ">>>" and split the string
    args = file_path_and_content.strip().split(">>>")
    if len(args) == 2:
        file_path = args[0][3:]
        content = args[1]
    else:
        return f"Error: Invalid input format. The input should be in the format: [file_path]content. args: {args}. Length: {len(args)}"

    project_dir = "./data/project"
    file_full_path = os.path.join(project_dir, file_path)
    try:
        with open(file_full_path, "w") as file:
            file.write(content)
        return f"File updated: {file_path}"
    except IOError:
        return f"Error: Unable to update the file: {file_path}"

class cuda_compilation_args(BaseModel):
    param: str = Field(description="""Provide always empty string.""")
    # param: Optional[str] = Field(
    #     None, 
    #     description="""Provide an empty string or None. Both inputs are acceptable."""
    #     )

def cuda_compilation(param=None):
    """
    This function compiles the project using the subproccess call:
    nvcc \
        -diag-suppress 1444 \
        -diag-suppress 550 \
        -G \
        -g data/project/source/main.cu \
        -arch=sm_86 \
        -I./data/project/source/include/ \
        -o data/project/out/program 2> data/project/out/build.log
    """
    program_path = "./data/project/out/program"
    # Remove program if exists
    if os.path.exists(program_path):
        os.remove(program_path)

    # Compile the project
    source = "./data/project/source/main.cu"
    include = "./data/project/source/include/"
    log = "./data/project/out/build.log"
    supress_flags = "-diag-suppress 1444 -diag-suppress 550"
    command = f"nvcc {supress_flags} -G -g {source} -arch=sm_86 -I{include} -o {program_path} 2> {log}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()

    # Read the log
    with open(log, "r") as file:
        log_content = file.read()

    # If log is empty, then the compilation was successful
    if len(log_content) == 0:
        return "Log is empty. Compilation successful."
    else:
        return log_content
    
    
class run_program_args(BaseModel):
    param: str = Field(description="""Provide empty string. There is no input required.""")

def run_program(param=None):
    """
    This function runs the program using the subproccess call:
    ./data/project/out/program
    """
    program_path = "./data/project/out/program"
    if os.path.exists(program_path):
        process = subprocess.Popen(program_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        return process.stdout.read().decode("utf-8")
    else:
        return "Error: Program not found."
