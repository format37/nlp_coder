from typing import Optional, Union
from pathlib import Path
import logging
from pydantic import BaseModel, Field
from langchain_community.tools import StructuredTool


class FileReader:
    """
    A class to safely read files with support for different encodings and error handling.
    """
    def __init__(self, default_encoding: str = 'utf-8'):
        """
        Initialize the FileReader.
        
        Args:
            default_encoding (str): Default encoding to use when reading files
        """
        self.default_encoding = default_encoding
        self.logger = logging.getLogger(__name__)

    def read_file(
        self,
        file_path: Union[str, Path],
        encoding: Optional[str] = None,
        binary: bool = False
    ) -> dict:
        """
        Read a file and return its contents.
        
        Args:
            file_path: Path to the file
            encoding: Character encoding to use (overrides default_encoding if provided)
            binary: If True, read file in binary mode
            
        Returns:
            dict: Dictionary containing:
                - success (bool): Whether the read operation was successful
                - content (Union[str, bytes]): File contents
                - error (str): Error message if any
        """
        file_path = Path(file_path)
        result = {
            "success": False,
            "content": None,
            "error": ""
        }

        if not file_path.exists():
            result["error"] = f"File not found: {file_path}"
            self.logger.error(result["error"])
            return result

        try:
            mode = 'rb' if binary else 'r'
            encoding_to_use = None if binary else (encoding or self.default_encoding)
            
            with open(file_path, mode=mode, encoding=encoding_to_use) as f:
                result["content"] = f.read()
                result["success"] = True
                
        except UnicodeDecodeError as e:
            result["error"] = f"Encoding error: {str(e)}. Try different encoding or binary mode."
            self.logger.error(result["error"])
            
        except Exception as e:
            result["error"] = f"Error reading file: {str(e)}"
            self.logger.error(result["error"])
            
        self.logger.debug(f"File read result: {result}")
        return result


class FileReaderToolArgs(BaseModel):
    """Arguments for the file reader tool."""
    file_path: str = Field(description="Path to the file to read.")
    encoding: Optional[str] = Field(
        None, 
        description="Character encoding to use. Default is 'utf-8'."
    )
    binary: bool = Field(
        False,
        description="If True, read file in binary mode. Default is False."
    )


async def file_reader_tool_coroutine(
    file_path: str,
    encoding: Optional[str] = None,
    binary: bool = False
) -> str:
    """
    Coroutine for reading files that can be used as a LangChain tool.
    
    Args:
        file_path: Path to the file to read
        encoding: Character encoding to use
        binary: If True, read file in binary mode
        
    Returns:
        str: File contents if successful, error message if not
    """
    reader = FileReader()
    result = reader.read_file(file_path, encoding, binary)
    
    if result["success"]:
        # For binary content, return base64 encoded string or handle as needed
        if binary and isinstance(result["content"], bytes):
            import base64
            return base64.b64encode(result["content"]).decode('utf-8')
        return str(result["content"])
    else:
        return result["error"]

# Create the LangChain tool
tool_file_reader = StructuredTool.from_function(
    coroutine=file_reader_tool_coroutine,
    name="file_reader",
    description="Read the contents of a file at the specified path.",
    args_schema=FileReaderToolArgs,
)


# Example usage
if __name__ == "__main__":
    # Create a reader instance
    reader = FileReader()
    
    # Example: Reading a text file
    text_result = reader.read_file("solution_4o.py")
    if text_result["success"]:
        print("File contents:", text_result["content"])
    else:
        print("Error:", text_result["error"])
    
    # # Example: Reading a binary file
    # binary_result = reader.read_file("example.jpg", binary=True)
    # if binary_result["success"]:
    #     print("Binary file size:", len(binary_result["content"]), "bytes")
    # else:
    #     print("Error:", binary_result["error"])
