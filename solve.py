import os
from openai import OpenAI
import anthropic
from structures import (
    Solution,
    SolutionRepresentation,
    Evaluation,
    EvaluationRepresentation
)
from structed_output_extended import structure_output_completion
from files import (
    create_project_files, 
    create_build_script, 
    create_run_script, 
    build_project, 
    run_project,
    read_log_file
)
import json

def main():
    
    run_count_limit = 10
    if "OPENAI_API_KEY" not in os.environ or "ANTHROPIC_API_KEY" not in os.environ:
        print("One of the API keys is missing. Please provide the API keys. For example:")
        print("export OPENAI_API_KEY=")
        print("export ANTHROPIC_API_KEY=")

    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = input("Enter your OpenAI API key (or Use 'export OPENAI_API_KEY=your-api-key' to set the API key): ")

    if "ANTHROPIC_API_KEY" not in os.environ:
        os.environ["ANTHROPIC_API_KEY"] = input("Enter your Anthropic API key (or Use 'export ANTHROPIC_API_KEY=your-api-key) to set the API key: ")

    client_openai = OpenAI()
    client_anthropic = anthropic.Anthropic()

    # Read user input from task.txt
    with open("task.txt", "r") as f:
        user_input = f.read()

    # Remove log.txt if it exists
    if os.path.exists("log.txt"):
        os.remove("log.txt")

    # Read system_content from system.txt
    with open("system.txt", "r") as f:
        system_content = f.read() # "You are a software engineer."
    messages=[
            # {"role": "system", "content": system_content},
            {"role": "user", "content": 
                [
                    {
                        "type": "text",
                        "text": f"{user_input}"
                    }
                ]
            }
        ]

    current_iteration = 0
    task_complete = False

    while not task_complete and current_iteration < run_count_limit:
        print(f"\nIteration: {current_iteration}")
        # Call with max_tokens=16384
        # completion = client_openai.beta.chat.completions.parse(
        #     model="gpt-4o-2024-08-06",
        #     messages = messages,
        #     max_tokens=16384,
        #     response_format=Solution,
        # )
        completion = structure_output_completion(
            model="o1-mini",
            messages=messages,
            response_format_representation=SolutionRepresentation,
            response_format=Solution
        )
        message = completion.choices[0].message
        # Extract token usage (prompt, completion, and total tokens)
        
        token_usage = completion.usage
        print(f"#### token_usage: {token_usage}")

        if message.parsed:
            # Log parsed message to log.txt
            with open("log.txt", "w") as f:
                f.write(str(message.parsed))
            solution = message.parsed

            # Create project directory
            os.makedirs("projects", exist_ok=True)
            project_dir_prototype = solution.project_name
            project_dir_prototype = project_dir_prototype.replace(" ", "_")
            project_dir_prototype = project_dir_prototype.replace("(", "-")
            project_dir_prototype = project_dir_prototype.replace(")", "-")
            project_dir = os.path.join("projects", project_dir_prototype)
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

            # Pack the solution into JSON
            solution_dict = solution.model_dump()        
            # Add build.log content if it exists
            build_log_content = read_log_file(os.path.join(project_dir, 'build.log'))
            if build_log_content is not None:
                solution_dict['build_log'] = build_log_content
            # Add run.log content if it exists
            run_log_content = read_log_file(os.path.join(project_dir, 'run.log'))
            if run_log_content is not None:
                solution_dict['run_log'] = run_log_content
            # Convert the dictionary to JSON
            solution_json = json.dumps(solution_dict, indent=2)        
            # You can now use solution_json for further LLM requests
            print("Packed solution into JSON:")
            print(solution_json)
            assistant_answer = solution_json
            # {"role": "assistant", "content": f"{answer}"}
            # messages.append({"role": "assistant", "content": f"{assistant_answer}"})
            messages.append({"role": "assistant", "content": 
            [
                {
                    "type": "text",
                    "text": f"Classify the following problem and return the result:\n{user_input}"
                }
            ]
            })

            # Evaluate solution
            print("\nEvaluating the solution...")
            user_input = f"Please, evaluate the solution: {solution_json}"
            # Call with max_tokens=16384
            # completion = client_openai.beta.chat.completions.parse(
            #     model="gpt-4o-2024-08-06",
            #     messages=[
            #         {"role": "system", "content": "You are a software engineer."},
            #         {"role": "user", "content": f"{user_input}"},
            #     ],
            #     max_tokens=16384,
            #     response_format=Evaluation,
            # )
            completion = structure_output_completion(
                model="o1-mini",
                messages=[
                    {"role": "user", "content": 
                        [
                            {
                                "type": "text",
                                "text": f"{user_input}"
                            }
                        ]
                    }
                ],
                response_format_representation=EvaluationRepresentation,
                response_format=Evaluation
            )

            message = completion.choices[0].message
            if message.parsed:
                # Log parsed message to log.txt
                with open(f"{project_dir}/log.txt", "a") as f:
                    f.write(f"\n[{current_iteration}] {str(message.parsed)}")
                evaluation = message.parsed
                # print(f"result_short_overview: {evaluation.result_short_overview}")
                # print(f"task_complete: {evaluation.task_complete}")
                task_complete = evaluation.task_complete
                user_content = f"Expected output: {evaluation.expected_output}\nActual output: {evaluation.actual_output}\nOverview: {evaluation.result_short_overview}\nTask complete: {evaluation.task_complete}"
                if not task_complete:
                    # Call anthropic to provide the user suggestions
                    # temperature=0,

                    # claude-3-5-sonnet-20240620
                    # 8192 output tokens is in beta and requires the header anthropic-beta: max-tokens-3-5-sonnet-2024-07-15. 
                    # If the header is not specified, the limit is 4096 tokens.
                    # Read advisor_content from advisor.txt
                    with open("advisor.txt", "r") as f:
                        advisor_content = f.read()

                    claude_message = client_anthropic.messages.create(
                        model="claude-3-5-sonnet-20240620",
                        max_tokens=4096,
                        system=advisor_content,
                        messages=[
                            {
                                "role": "user",
                                "content": f"{user_content}."
                            }
                        ]
                    )
                    # Check if content is a list and join it if necessary
                    # if isinstance(claude_message.content, list):
                    #     claude_response = ' '.join(claude_message.content)
                    # else:
                    #     claude_response = claude_message.content
                    # Extract the text from the first (and likely only) TextBlock in the list
                    claude_response = claude_message.content[0].text
                    print(f"claude_response type: {type(claude_response)}")
                    print(f"claude_response: {claude_response}")
                    user_content += claude_response
                # user_answer = {"role": "user", "content": user_content}
                user_answer = {"role": "user", "content": 
                    [
                        {
                            "type": "text",
                            "text": f"{user_content}"
                        }
                    ]
                }
                messages.append(user_answer)

            # Dump messages into {current_iteration}_messages.json
            with open(f"{project_dir}/{current_iteration}_messages.json", "w") as f:
                f.write(json.dumps(messages, indent=2))

            # Copy task.txt, system.txt and advisor.txt from local to the project directory
            destination_file_path = f"{project_dir}/task.txt"
            if not os.path.exists(destination_file_path):
                cmd = f"cp task.txt {destination_file_path}"
                print(f'caling: {cmd}')
                os.system(cmd)
            destination_file_path = f"{project_dir}/system.txt"
            if not os.path.exists(destination_file_path):
                cmd = f"cp system.txt {destination_file_path}"
                print(f'caling: {cmd}')
                os.system(cmd)
            destination_file_path = f"{project_dir}/advisor.txt"
            if not os.path.exists(destination_file_path):
                cmd = f"cp advisor.txt {destination_file_path}"
                print(f'caling: {cmd}')
                os.system(cmd)

            current_iteration += 1

        else:
            print(message.refusal)
            break

if __name__ == "__main__":
    main()