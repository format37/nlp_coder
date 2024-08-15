# AI-Powered Coding Assistant

This project showcases an innovative script that leverages the power of AI to automatically solve coding problems. By utilizing OpenAI's GPT-4 and Anthropic's Claude, this tool can generate, build, and run code solutions with minimal human intervention.

## Features

- Utilizes OpenAI's new `response_format` feature for structured output
- Implements an iterative problem-solving approach
- Integrates both GPT-4 and Claude AI models for comprehensive assistance
- Automatically generates, builds, and runs code solutions
- Evaluates output against expected results
- Provides AI-driven error correction and optimization

## How It Works

1. Takes a coding prompt from `task.txt`
2. Generates a solution using GPT-4
3. Creates project files and build/run scripts
4. Attempts to build and run the generated program
5. Evaluates the output against expected results
6. If unsuccessful, Claude AI suggests improvements
7. Repeats the process until the task is completed or reaches 10 iterations

## Prerequisites

- Python 3.7+
- OpenAI API key
- Anthropic API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai-powered-coding-assistant.git
   cd ai-powered-coding-assistant
   ```

2. Install the required dependencies:
   ```
   pip install openai anthropic pydantic
   ```

3. Set up your API keys as environment variables:
   ```
   export OPENAI_API_KEY='your-openai-api-key'
   export ANTHROPIC_API_KEY='your-anthropic-api-key'
   ```

## Usage

1. Edit the `task.txt` file to include your coding prompt or problem description.

2. Edit the `system.txt` file to set the system message for the AI (default is "You are a software engineer.").

3. Run the main script:
   ```
   python main.py
   ```

4. The script will create a new directory in the `projects` folder for each iteration, containing the generated code, build logs, and run logs.

5. Check the output in the console and the generated files to see the results and any suggestions for improvement.

## Project Structure

- `main.py`: The main script that orchestrates the AI-powered coding process
- `structures.py`: Defines the data structures used in the project
- `files.py`: Contains utility functions for file operations and project management
- `task.txt`: The input file where you specify your coding task
- `system.txt`: The file containing the system message for the AI

## Limitations

- The script is limited to 10 iterations per run to prevent infinite loops
- The effectiveness of the solution depends on the clarity of the task description and the capabilities of the AI models
- Some complex tasks may require human intervention or further refinement

## Contributing

Contributions to improve the script or extend its capabilities are welcome. Please feel free to submit issues or pull requests.

## License

[MIT License](LICENSE)

## Acknowledgments

- OpenAI for providing the GPT-4 API
- Anthropic for the Claude AI API

---

This project is for educational and research purposes only. Please use responsibly and in accordance with the API providers' terms of service.
