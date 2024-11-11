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

class TextFileReaderArgs(BaseModel):
    file_list: List[int] = Field(description="List of file IDs")
    
class AddToolArgs(BaseModel):
    a: int = Field(description="First number")
    b: int = Field(description="Second number")

async def text_file_reader(file_list: List[str]) -> str:
    # Your asynchronous code to read text files
    print(f"# text_file_reader request.\ntype: {type(file_list)}\nfile_list: {file_list}")
    return "These files contains these numbers: '298376837456\n658498465213546'"

async def add_tool(a: int, b: int) -> int:
    print(f"add_tool request: a: {a}, b: {b}")
    return a + b

async def conversation():
    add_tool_object = StructuredTool.from_function(
        coroutine=add_tool,
        name="add_two_numbers",
        description="Add two numbers",
        args_schema=AddToolArgs,
    )
    text_file_reader_tool = StructuredTool.from_function(
        coroutine=text_file_reader,
        name="read_text_file",
        # description = 'Read files from list of ids in format "[id1, id2, ...]\n\n". Input should end with 2 new lines.',
        description = 'Read files from list of ids in format "[id1, id2, ...]".',
        args_schema=TextFileReaderArgs,
    )
    tools = []
    tools.append(add_tool_object)
    tools.append(text_file_reader_tool)
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
    system_prompt = "You are helpful assistant."
    chat_history = []
    
    input = 'Please read files with ids: 12, 37 and tell what they contains'
    result = await agent_executor.ainvoke(
        {
            "input": input,
            "chat_history": chat_history,
            "system_prompt": system_prompt,
        }
    )
    chat_history.append(HumanMessage(content=input))
    chat_history.append(AIMessage(content=result["output"]))
    print(f"<< result.output: {result['output']}")

    input = "Now please, add these numbers"
    result = await agent_executor.ainvoke(
        {
            "input": input,
            "chat_history": chat_history,
            "system_prompt": system_prompt,
        }
    )
    chat_history.append(HumanMessage(content=input))
    chat_history.append(AIMessage(content=result["output"]))
    print(f"<< result.output: {result['output']}")
    
    # 65,879,684,205,1002 or 658796842051002

    print(f"chat_history: {chat_history}")

async def main():
    await conversation()

asyncio.run(main())
