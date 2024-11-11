from typing import Optional, Union
from pathlib import Path
import logging
from pydantic import BaseModel, Field
from langchain_community.tools import StructuredTool


class FileSaver:
    """
    A class to safely save files with support for different encodings and error handling.
    """
    def __init__(self, default_encoding: str = 'utf-8'):
        """
        Initialize the FileSaver.
        
        Args:
            default_encoding (str): Default encoding to use when writing files
        """
        self.default_encoding = default_encoding
        self.logger = logging.getLogger(__name__)

    def save_file(
        self,
        file_path: Union[str, Path],
        content: Union[str, bytes],
        encoding: Optional[str] = None,
        binary: bool = False,
        overwrite: bool = False
    ) -> dict:
        """
        Save content to a file.
        
        Args:
            file_path: Path where to save the file
            content: Content to write (string or bytes)
            encoding: Character encoding to use (overrides default_encoding if provided)
            binary: If True, write file in binary mode
            overwrite: If True, overwrite existing file; if False, raise error if file exists
            
        Returns:
            dict: Dictionary containing:
                - success (bool): Whether the write operation was successful
                - error (str): Error message if any
        """
        file_path = Path(file_path)
        result = {
            "success": False,
            "error": ""
        }

        # # Ensure we're not trying to write outside the current directory
        # try:
        #     file_path = file_path.resolve()
        #     current_dir = Path.cwd().resolve()
        #     if not str(file_path).startswith(str(current_dir)):
        #         result["error"] = "Cannot write files outside the current directory"
        #         self.logger.error(result["error"])
        #         return result
        # except Exception as e:
        #     result["error"] = f"Path resolution error: {str(e)}"
        #     self.logger.error(result["error"])
        #     return result

        # Check if file exists and handle overwrite flag
        if file_path.exists() and not overwrite:
            result["error"] = f"File already exists: {file_path}. Set overwrite=True to overwrite."
            self.logger.error(result["error"])
            return result

        try:
            # Handle escaped newlines in content
            if isinstance(content, str):
                # Detect if content contains escaped newlines
                if '\\n' in content and '\n' not in content:
                    content = content.encode('utf-8').decode('unicode_escape')
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Set up write mode and encoding
            mode = 'wb' if binary else 'w'
            encoding_to_use = None if binary else (encoding or self.default_encoding)

            # Validate content type
            if binary and not isinstance(content, bytes):
                content = content.encode(encoding_to_use or self.default_encoding)
            elif not binary and isinstance(content, bytes):
                content = content.decode(encoding_to_use or self.default_encoding)

            # Write the file
            with open(file_path, mode=mode, encoding=encoding_to_use) as f:
                f.write(content)
                result["success"] = True

        except UnicodeEncodeError as e:
            result["error"] = f"Encoding error: {str(e)}. Try different encoding or binary mode."
            self.logger.error(result["error"])

        except Exception as e:
            result["error"] = f"Error writing file: {str(e)}"
            self.logger.error(result["error"])

        self.logger.debug(f"File write result: {result}")
        return result


class FileSaverToolArgs(BaseModel):
    """Arguments for the file saver tool."""
    file_path: str = Field(description="Path where to save the file.")
    content: str = Field(description="Content to write to the file.")
    encoding: Optional[str] = Field(
        None, 
        description="Character encoding to use. Default is 'utf-8'."
    )
    binary: bool = Field(
        False,
        description="If True, write file in binary mode. Default is False."
    )
    overwrite: bool = Field(
        False,
        description="If True, overwrite existing file. Default is False."
    )


async def file_saver_tool_coroutine(
    file_path: str,
    content: str,
    encoding: Optional[str] = None,
    binary: bool = False,
    overwrite: bool = False
) -> str:
    """
    Coroutine for saving files that can be used as a LangChain tool.
    
    Args:
        file_path: Path where to save the file
        content: Content to write to the file
        encoding: Character encoding to use
        binary: If True, write file in binary mode
        overwrite: If True, overwrite existing file
        
    Returns:
        str: Success message if successful, error message if not
    """
    saver = FileSaver()
    
    # Handle base64 encoded content if binary mode is True
    if binary and not isinstance(content, bytes):
        try:
            import base64
            content = base64.b64decode(content)
        except Exception as e:
            return f"Error decoding base64 content: {str(e)}"
    
    result = saver.save_file(file_path, content, encoding, binary, overwrite)
    
    if result["success"]:
        return f"File successfully saved to {file_path}"
    else:
        return result["error"]

# Create the LangChain tool
tool_file_saver = StructuredTool.from_function(
    coroutine=file_saver_tool_coroutine,
    name="file_saver",
    description="Save content to a file at the specified path.",
    args_schema=FileSaverToolArgs,
)


# Example usage
if __name__ == "__main__":
    # Create a saver instance
    saver = FileSaver()
    
    # Example: Saving a text file
    text_content = """
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
"""
    text_result = saver.save_file(
        "example_script.py",
        text_content,
        overwrite=True
    )
    
    if text_result["success"]:
        print("Text file saved successfully")
    else:
        print("Error:", text_result["error"])
    
    # Example: Saving a binary file
    binary_content = b"Hello, Binary World!"
    binary_result = saver.save_file(
        "example.bin",
        binary_content,
        binary=True,
        overwrite=True
    )
    
    if binary_result["success"]:
        print("Binary file saved successfully")
    else:
        print("Error:", binary_result["error"])