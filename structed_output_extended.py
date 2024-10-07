from openai import OpenAI
from typing import Literal, List, Union, Any
import logging
import sys

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add a stream handler to print log messages to console
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def structure_output_completion(
    model: str,
    messages: List[dict],
    response_format_representation: Any,
    response_format: Any
) -> Any:
    client = OpenAI()
    
    logger.info(f"[1] Calling completions for model: {model}")
    
    # Copy messages to messages_with_format
    messages_with_format = messages.copy()
    messages_with_format[-1]["content"][0]["text"] += f"\nResponse format is JSON, according to this structure:\n{response_format_representation}"
    
    initial_completion = client.beta.chat.completions.parse(
        model=model,
        messages=messages_with_format
    )
    
    # Then, structure the output using gpt-4o-2024-08-06
    structuring_messages = [
        {"role": "system", "content": "You are an expert in structuring data according to given formats."},
        {"role": "user", "content": f"Given the following data, format it with the given response format: {initial_completion.choices[0].message.content}"}
    ]

    logger.info(f"[1] Calling parsing from model: gpt-4o-2024-08-06")
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=structuring_messages,
        response_format=response_format
    )
    
    # return completion.choices[0].message
    return completion