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
        f.write(solution.build_script)
        if not solution.build_script.strip():
            f.write("# No build steps required\n")
    os.chmod(build_script_path, 0o755)

def create_run_script(solution: Solution, project_dir: str):
    run_script_path = os.path.join(project_dir, 'run.sh')
    with open(run_script_path, 'w') as f:
        f.write("#!/bin/bash\n")  # Add shebang line
        f.write(solution.run_script)
    os.chmod(run_script_path, 0o755)  # Make the script executable

def build_project(project_dir: str):
    build_script_path = os.path.join(project_dir, 'build.sh')
    with open(build_script_path, 'r') as f:
        content = f.read().strip()
    
    if content == "#!/bin/bash\n# No build steps required":
        return 0, "No build required", ""
    
    result = subprocess.run([build_script_path], cwd=project_dir, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def run_project(project_dir: str, timeout: int):
    run_script_path = os.path.join(project_dir, 'run.sh')
    try:
        result = subprocess.run(['/bin/bash', run_script_path], cwd=project_dir, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Execution timed out after {timeout} seconds"
    except Exception as e:
        return 1, "", f"Error executing run script: {str(e)}"