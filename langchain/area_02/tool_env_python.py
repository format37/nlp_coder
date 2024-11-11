import subprocess
from typing import Optional, Union, Dict, List
import json
from pathlib import Path
import logging
import asyncio
from pydantic import BaseModel, Field
from typing import List
from langchain_community.tools import StructuredTool

class ScriptRunner:
    """
    A class to safely run Python scripts with timeout and parameter support.
    """
    def __init__(self, default_timeout: int = 60):
        """
        Initialize the ScriptRunner.
        
        Args:
            default_timeout (int): Default timeout in seconds for script execution
        """
        self.default_timeout = default_timeout
        self.logger = logging.getLogger(__name__)

    def run_script(
        self,
        script_path: Union[str, Path],
        params: Optional[Union[Dict, List]] = None,
        timeout: Optional[int] = None,
        python_path: str = "python"
    ) -> dict:
        """
        Run a Python script with parameters and timeout.
        
        Args:
            script_path: Path to the Python script
            params: Dictionary or list of parameters to pass to the script
            timeout: Timeout in seconds (overrides default_timeout if provided)
            python_path: Path to Python interpreter
            
        Returns:
            dict: Dictionary containing:
                - success (bool): Whether the execution was successful
                - output (str): Script output (stdout)
                - error (str): Error message if any (stderr)
                - timeout_occurred (bool): Whether execution timed out
                - return_code (int): Script return code
        """
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
            
        timeout = timeout or self.default_timeout
        cmd = [python_path, str(script_path)]
        
        # Convert parameters to command line arguments
        if params:
            if isinstance(params, dict):
                # Convert dict to JSON string and pass as single argument
                cmd.append(json.dumps(params))
            elif isinstance(params, list):
                # Add list items as separate arguments
                cmd.extend(str(param) for param in params)
            else:
                raise ValueError("params must be either a dictionary or a list")

        result = {
            "success": False,
            "output": "",
            "error": "",
            "timeout_occurred": False,
            "return_code": None
        }

        try:
            # Run the script with timeout
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                result.update({
                    "success": process.returncode == 0,
                    "output": stdout,
                    "error": stderr,
                    "return_code": process.returncode
                })
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                result.update({
                    "timeout_occurred": True,
                    "error": f"Script execution timed out after {timeout} seconds",
                    "output": stdout,
                    "return_code": -1
                })
                
        except Exception as e:
            result.update({
                "error": f"Error running script: {str(e)}",
                "return_code": -1
            })
            
        self.logger.debug(f"Script execution result: {result}")
        return result

class PythonToolArgs(BaseModel):
    script_path: str = Field(description="Script path.")
    # timeout: Optional[int] = Field(description="Timeout in seconds. Default is 60 seconds")
    timeout: int = Field(description="Timeout in seconds.")
    # params: Union[Dict, List] = Field(description="Script parameters.")
    params: List = Field(description="Script parameters.")

async def python_tool_coroutine(script_path: str, timeout: Optional[int] = None, params: Optional[Union[Dict, List]] = []) -> str:
    runner = ScriptRunner(default_timeout=60)
    result = runner.run_script(script_path, params, timeout)
    if result["success"]:
        return result["output"]
    else:
        return result["error"]
    
tool_python = StructuredTool.from_function(
    coroutine=python_tool_coroutine,
    name="python",
    description = '',
    args_schema=PythonToolArgs,
)

# Example usage
if __name__ == "__main__":
    # Create a runner instance with 30 second default timeout
    runner = ScriptRunner(default_timeout=30)
    
    # # Example with dictionary parameters
    # dict_result = runner.run_script(
    #     "your_script.py",
    #     params={"input_file": "data.csv", "max_rows": 1000},
    #     timeout=45  # Override default timeout
    # )
    
    # Example with list parameters
    list_result = runner.run_script(
        "solution_4o.py",
        # params=["--input", "data.csv", "--max-rows", "1000"]
        timeout=10  # Override default timeout
    )
    
    # # Check results
    # if dict_result["success"]:
    #     print("Script output:", dict_result["output"])
    # else:
    #     print("Error:", dict_result["error"])
        
    # if dict_result["timeout_occurred"]:
    #     print("Script execution timed out")
    if list_result["success"]:
        print("Script output:", list_result["output"])
    else:
        print("Error:", list_result["error"])
