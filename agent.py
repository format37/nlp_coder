# -*- coding: utf-8 -*-
import json
import sys
import warnings
from pydantic import BaseModel, Field
from langchain.agents import Tool, initialize_agent
# from langchain.agents import load_tools
# from langchain.chains import RetrievalQA
# from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.tools import ShellTool, DuckDuckGoSearchRun
from langchain.schema import HumanMessage, SystemMessage, AIMessage
# from langchain.globals import set_debug
# set_debug(True)
# import tiktoken
# from llm_cost_estimation import count_tokens
# Import things that are needed generically
# from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_community.llms import Ollama
from coder_tools import (
    get_file_list_args,
    get_file_list,
    show_files_content_args,
    show_files_content,
    remove_file_args,
    remove_file,
    update_file_args,
    update_file,
    cuda_compilation_args,
    cuda_compilation,
    run_program_args,
    run_program
)


class ConfigLoader:
    def __init__(self, config_filename='config.json'):
        self.config_filename = config_filename
        self.config = self.load_config()
        """if self.config['openai']['api_key']=='':
            self.config['openai']['api_key']=input("Please enter your OpenAI API key: ")"""

    def load_config(self):
        with open(self.config_filename, 'r') as file:
            return json.load(file)


class DocumentProcessor:
    def __init__(self, config):
        self.config = config

    def process_documents(self):
        context_path = self.config['context']['path']
        loader = DirectoryLoader(context_path, glob="*", loader_cls=TextLoader)
        docs = loader.load()
        embeddings = OpenAIEmbeddings(openai_api_key=self.config['openai']['api_key'])
        text_splitter = RecursiveCharacterTextSplitter()
        documents = text_splitter.split_documents(docs)
        vector = DocArrayInMemorySearch.from_documents(documents, embeddings)
        return vector.as_retriever()


class ChatAgent:
    def __init__(self, config, retriever):
        self.config = config
        self.retriever = retriever
        self.agent = self.initialize_agent()

    def initialize_agent(self):
        """llm = ChatOpenAI(
            openai_api_key=self.config['openai']['api_key'],
            model=self.config['openai']['model'],
            temperature=self.config['openai']['temperature']
        )"""
        llm = Ollama(model="mistral")
        # requests_tools = load_tools(["requests_all"])
        shell_tool = ShellTool()
        shell_tool.description = shell_tool.description + f"args {shell_tool.args}".replace(
            "{", "{{"
        ).replace("}", "}}")
        """Tool(
                args_schema=DocumentInput,
                name='Additional context',
                description="Additional context that has been provided by user",
                func=RetrievalQA.from_chain_type(llm=llm, retriever=self.retriever),
            ),"""
        tools = [
            StructuredTool.from_function(
                func=get_file_list,
                name="Get list of files",
                description="Reads list of files recursively in the project folder",
                args_schema=get_file_list_args,
                return_direct=False,
                # coroutine= ... <- you can specify an async method if desired as well
            ),
            StructuredTool.from_function(
                func=show_files_content,
                name="Show the content of files, from the file list according to the mask",
                description="You need to provide a mask to filter the files. * will show all files. The content of the files is returned.",
                args_schema=show_files_content_args,
                return_direct=False,
                # coroutine= ... <- you can specify an async method if desired as well
            ),
            StructuredTool.from_function(
                func=remove_file,
                name="Remove file",
                description="The function removes the file from the project folder. You need to provide the path to the file.",
                args_schema=remove_file_args,
                return_direct=False,
                # coroutine= ... <- you can specify an async method if desired as well
            ),
            StructuredTool.from_function(
                func=update_file,
                name="Update file",
                description="The function updates the file in the project folder. Use [ and ] symbols to mark the file path. The input should be in the format: [file_path]content.",
                args_schema=update_file_args,
                return_direct=False,
                # coroutine= ... <- you can specify an async method if desired as well
            ),
            StructuredTool.from_function(
                func=cuda_compilation,
                name="Cuda compilation",
                description="The function compiles the  source/main.cu file.",
                args_schema=cuda_compilation_args,
                return_direct=False,
                # coroutine= ... <- you can specify an async method if desired as well
            ),
            StructuredTool.from_function(
                func=run_program,
                name="Run program",
                description="The function runs the program.",
                args_schema=run_program_args,
                return_direct=False,
                # coroutine= ... <- you can specify an async method if desired as well
            ),
        ]
        # 
        """DuckDuckGoSearchRun(),
            requests_tools[0]"""

        return initialize_agent(tools, llm, agent='chat-conversational-react-description', 
                                verbose=True, handle_parsing_errors=True)

    def run(self):
        chat_history = []
        # Add a system message to the chat history
        # tokens_total = 0
        # Read user_input from data/prompt.txt
        with open('data/prompt.txt', 'r') as file:
            user_input = file.read()
        while True:            
            # Update the chat history with the User input
            chat_history.append(HumanMessage(content=user_input))
            response = self.agent.run(input=user_input, chat_history=chat_history)            
            # Update the chat history with the Agent response
            chat_history.append(AIMessage(content=response))
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break


class DocumentInput(BaseModel):
    question: str = Field()


def main():
    if len(sys.argv) > 1:
        config_filename = sys.argv[1]
    else:
        config_filename = 'config.json'

    config_loader = ConfigLoader(config_filename)
    # document_processor = DocumentProcessor(config_loader.config)
    # retriever = document_processor.process_documents()
    retriever = None

    chat_agent = ChatAgent(config_loader.config, retriever)
    warnings.filterwarnings('ignore', category=UserWarning)
    chat_agent.run()


if __name__ == '__main__':
    main()
