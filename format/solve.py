import os
from openai import OpenAI
from structures import Solution
from files import (
    create_project_files, 
    create_build_script, 
    create_run_script, 
    build_project, 
    run_project
)

def main():
    
    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = input("Enter your OpenAI API key (or Use 'export OPENAI_API_KEY=your-api-key' to set the API key): ")

    client = OpenAI()

    user_input = """
    Please, implement a python3 function that calculates the sum of two numbers. The function should take two arguments and return the sum of the two numbers.
    Place the function in a separate file.
    The main file should import the function and call it with the arguments 3 and 5.
    """

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a software engineer."},
            {"role": "user", "content": f"{user_input}"},
        ],
        response_format=Solution,
    )

    message = completion.choices[0].message
    if message.parsed:
        # Log parsed message to log.txt
        with open("log.txt", "w") as f:
            f.write(str(message.parsed))
        solution = message.parsed

        # Create project directory
        os.makedirs("projects", exist_ok=True)
        project_dir = os.path.join("projects", solution.project_name)
        # Account the os.getcwd() in the project_dir
        project_dir = os.path.join(os.getcwd(), project_dir)
        # Create project directory
        os.makedirs(project_dir, exist_ok=True)        
        # with tempfile.TemporaryDirectory() as project_dir:
        create_project_files(solution, project_dir)
        create_build_script(solution, project_dir)
        create_run_script(solution, project_dir)

        print(f"Building project: {solution.project_name}")
        build_code, build_output, build_error = build_project(project_dir)
        if build_code != 0:
            print("Build failed:")
            print(build_error)
        elif build_output == "No build required":
            print("No build required")
        else:
            print("Build successful")

        print(f"\nRunning project: {solution.project_name}")
        run_code, run_output, run_error = run_project(project_dir, solution.run_timeout_seconds)
        if run_code != 0:
            print("Run failed:")
            print(run_error)
            if run_output:
                print("Output:")
                print(run_output)
        else:
            print("Run successful")
            print("Output:")
            print(run_output)

    else:
        print(message.refusal)

if __name__ == "__main__":
    main()