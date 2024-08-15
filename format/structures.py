from pydantic import BaseModel, Field
from typing import Literal, List, Union

class File(BaseModel):
    name: str
    content: str

class Solution(BaseModel):
    project_name: str
    description: str
    language: Literal["python3", "java", "c++", "c", "cuda"]
    files: List[File]
    build_script: str
    run_script: str
    run_timeout_seconds: int