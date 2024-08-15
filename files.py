import subprocess
import os
from structures import Solution

def create_project_files(solution: Solution, project_dir: str):
    for file in solution.files:
        file_path = os.path.join(project_dir, file.name)
        with open(file_path, 'w') as f:
            f.write(file.content)

def create_build_script(solution: Solution, project_dir: str):
    build_script_path = os.path.join(project_dir, 'build.sh')
    with open(build_script_path, 'w') as f:
        f.write("#!/bin/bash\n")  # Add shebang line
        if not solution.build_script.strip():
            f.write("# No build steps required\n")
        else:
            f.write(f"{solution.build_script} 2> build.log\n")        
    os.chmod(build_script_path, 0o755)

def create_run_script(solution: Solution, project_dir: str):
    run_script_path = os.path.join(project_dir, 'run.sh')
    with open(run_script_path, 'w') as f:
        f.write("#!/bin/bash\n")  # Add shebang line
        f.write(f"{solution.run_script} >> run.log\n")
    os.chmod(run_script_path, 0o755)  # Make the script executable

def build_project(project_dir: str):
    build_script_path = os.path.join(project_dir, 'build.sh')
    with open(build_script_path, 'r') as f:
        content = f.read().strip()
    
    if content == "#!/bin/bash\n# No build steps required":
        return 0, "No build required", ""
    
    # Remove build.log if it exists
    build_log_path = os.path.join(project_dir, 'build.log')
    if os.path.exists(build_log_path):
        os.remove(build_log_path)
    
    result = subprocess.run([build_script_path], cwd=project_dir, capture_output=True, text=True)
    
    # Read the build log
    build_log_content = ""
    if os.path.exists(build_log_path):
        with open(build_log_path, 'r') as f:
            build_log_content = f.read()
    
    return result.returncode, result.stdout, build_log_content

def run_project(project_dir: str, timeout: int):
    run_script_path = os.path.join(project_dir, 'run.sh')
    try:
        # Remove run.log if it exists
        run_log_path = os.path.join(project_dir, 'run.log')
        if os.path.exists(run_log_path):
            os.remove(run_log_path)
        result = subprocess.run(['/bin/bash', run_script_path], cwd=project_dir, capture_output=True, text=True, timeout=timeout)
        print("The process has finished expectedly.")
        # Read the run log
        run_log_content = ""
        if os.path.exists(run_log_path):
            with open(run_log_path, 'r') as f:
                run_log_content = f.read()
        
        return result.returncode, result.stdout, run_log_content
    except subprocess.TimeoutExpired:
        print("Timeout expired. Trying to kill the process...")
        # Try to kill the process
        try:
            subprocess.run(['pkill', '-f', run_script_path], capture_output=True, text=True)
        except Exception as e:
            return 1, "", f"Error killing process: {str(e)}"
        return 1, "", f"Execution timed out after {timeout} seconds"
    except Exception as e:
        return 1, "", f"Error executing run script: {str(e)}"
    
def read_log_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read()
    return None