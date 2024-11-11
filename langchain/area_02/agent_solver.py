from langchain_ollama import ChatOllama
from langchain.tools import Tool
from langchain_community.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage
from io import StringIO
from contextlib import redirect_stdout
from pydantic import BaseModel, Field
from typing import List
import asyncio

async def solve(system_prompt, request_text, tools):
    print("++ Solve agent ++")
    print(f"system_prompt: {system_prompt}")
    print(f"request_text: {request_text}")
    # tools = []
    # tools.append(tool_python)
    # tools.append(tool_file_reader)
    # tools.append(tool_file_saver)

    prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "{system_prompt}"),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
    llm = ChatOllama(model="qwen2.5-coder:7b-instruct")
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    chat_history = []
    result = await agent_executor.ainvoke(
        {
            "input": request_text,
            "chat_history": chat_history,
            "system_prompt": system_prompt,
        }
    )
    chat_history.append(HumanMessage(content=request_text))
    chat_history.append(AIMessage(content=result["output"]))
    # print(f"<< result.output: {result['output']}")
    # print(f"chat_history: {chat_history}")
    print("-- Solve agent --")
    return result["output"]

async def main():
    system_prompt = "You are helpful assistant."
    request = 'Please run the script "solution_4o.py". Evaluate results, read the original script try to improve the solution. Save the solution to the new file with name solution_5o.py and try again.'
    await solve()

if __name__ == "__main__":
    asyncio.run(main())
