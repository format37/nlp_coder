import asyncio
from agent_solver import solve
from tool_env_python import ScriptRunner
# from tool_env_python import tool_python
# from tool_env_file_reader import tool_file_reader
# from tool_env_file_saver import tool_file_saver

import json
from dataclasses import dataclass

@dataclass
class SolutionResult:
    solved: bool
    following_requirements: bool
    output: str = ""  # Optional with default value
    review: str = ""  # Optional with default value

    @classmethod
    def from_json(cls, json_text: str) -> 'SolutionResult':
        # Find the last JSON block in the text
        start = json_text.rfind('{')
        end = json_text.rfind('}') + 1
        
        if start != -1 and end != -1:
            json_str = json_text[start:end]
            data = json.loads(json_str)
            return cls(
                solved=data['solved'],
                following_requirements=data['following_requirements'],
                output=data.get('output', ''),  # Using .get() with default value
                review=data.get('review', '')   # Using .get() with default value
            )
        return cls(solved=False, following_requirements=False)  # Default instance if parsing fails

async def main():
    solved = False
    following_requirements = False
    while not solved or not following_requirements:
        system_prompt = """You are Python developer.
You able to save and run your scripts.
You have the following tools:
file_saver
"""
        # Read the initial task from the file
        with open("initial_task.md", "r") as f:
            initial_task = f.read()
        tools = []
        response = await solve(system_prompt, initial_task, tools)
        # Remove starters like ```python and enders like ```
        if response.startswith("```python"):
            response = response[9:]
        if response.endswith("```"):
            response = response[:-3]
        # Save the script to the file
        with open("solution.py", "w") as f:
            f.write(response)
            print("Script saved to the file solution.py")
        
        # Run the script
        runner = ScriptRunner(default_timeout=10)
        list_result = runner.run_script(
            "solution.py",
            # params=["--input", "data.csv", "--max-rows", "1000"]
            # timeout=10  # Override default timeout
        )
        
        # # # Check results
        # if dict_result["success"]:
        #     print("Script output:", dict_result["output"])
        # else:
        #     print("Error:", dict_result["error"])
            
        # if dict_result["timeout_occurred"]:
        #     print("Script execution timed out")
            
        if list_result["success"]:
            # print("Script output:", list_result["output"])
            output = list_result["output"]
        else:
            # print("Error:", list_result["error"])
            output = list_result["error"]
        if list_result["timeout_occurred"]:
            output = "Script execution timed out"
            # print("Script execution timed out")
        
        # Ask to run the script
        request = """## Initial task:
""" + initial_task
        request += """
### Script:
```
"""
        request += response
        request += "```"
        request += """### Script output:
```
""" + output + """
```"""
        # Run the solution.py script using python tool.
        request += """
## Current task:
Provide the 
* Flag on was it solved or not? Check carefully according to the initial task, solution logic and outputs.
* Flag does it following the initial task requirements? Check carefully according to the initial task, solution logic and outputs.
* Your review
It is CRUCIAL to use JSON format for answer: {solved: true/false, "following_requirements": true/false, "review": "your review"}.
This JSON will be parsed later."""
        tools = []
        # tools.append(tool_python)
        response = await solve(system_prompt, request, tools)
        # print(response)
        if response.startswith("```json"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        result = SolutionResult.from_json(response)
        print(f"Solved ({type(result.solved)}): {result.solved}")
        print(f"Following requirements ({type(result.following_requirements)}): {result.following_requirements}")
        print(f"Review: {result.review}")
        print(f"Output: {result.output}")
        solved = result.solved
        following_requirements = result.following_requirements
    
    print("Task is solved and following initial requirements")

if __name__ == "__main__":
    asyncio.run(main())
