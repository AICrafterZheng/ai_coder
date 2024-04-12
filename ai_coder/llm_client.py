import instructor
import inspect
from pydantic import BaseModel, Field
from openai import OpenAI, AzureOpenAI
from ai_coder.prompts import SYS_PROMPT
from typing import List
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from ai_coder.logger import logger
# Load environment variables
load_dotenv()

USE_AZURE_OPENAI_API = os.getenv("USE_AZURE_OPENAI_API", "False").lower() == "true"
USE_ANTHROPIC = os.getenv("USE_ANTHROPIC", "False").lower() == "true"
USE_OPENAI_API = os.getenv("USE_OPENAI_API", "False").lower() == "true"
USE_OPENROUTER_API = os.getenv("USE_OPENROUTER_API", "False").lower() == "true"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "")
AZURE_OPENAI_API_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_API_DEPLOYMENT_NAME", "")
AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "")

logger.info(f"USE_OPENAI_API: {USE_OPENAI_API}")
logger.info(f"USE_ANTHROPIC: {USE_ANTHROPIC}")
logger.info(f"USE_AZURE_OPENAI_API: {USE_AZURE_OPENAI_API}")
logger.info(f"USE_OPENROUTER_API: {USE_OPENROUTER_API}")

# Define the function structure
class FuncInfo(BaseModel):
    imports: List[str] = Field([], description="List of imports")
    name: str = Field(..., description="Name of the function")
    parameters: List[str] = Field(..., description="Function parameters")
    body: str = Field(..., description="Function body, not including the function definition")
    return_type: str = Field(..., description="Return type of the function")

client = None
llm = None

if USE_OPENAI_API:
    logger.info("Using OpenAI API")
    llm = OpenAI(api_key=OPENAI_API_KEY)
    client = instructor.patch(llm)
elif USE_ANTHROPIC:
    logger.info("Using Anthropic API")
    llm = Anthropic(api_key=ANTHROPIC_API_KEY)
    client = instructor.from_anthropic(llm)
elif USE_AZURE_OPENAI_API:
    logger.info("Using Azure OpenAI API")
    llm = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_API_BASE
    )
    client = instructor.patch(llm)
elif USE_OPENROUTER_API:
    logger.info("Using OpenRouter API")
    llm = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    client = instructor.patch(llm)

def generate_func(user_input: str) -> FuncInfo:
    if client is None:
        raise Exception("No OpenAI client found. Please set USE_OPENAI_API, USE_ANTHROPIC or USE_AZURE_OPENAI_API environment variable to True")
    func_info = None

    if USE_OPENAI_API:
        try:
            func_info = client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0,
                response_model=FuncInfo,
                messages=[{"role": "system", "content": SYS_PROMPT}, {"role": "user", "content": user_input}],
            )
        except Exception as e:
            logger.error(f"generate_func Error: {e}")
            raise Exception(e)
    elif USE_AZURE_OPENAI_API:
        func_info = client.chat.completions.create(
            model= AZURE_OPENAI_API_DEPLOYMENT_NAME,
            temperature=0,
            response_model=FuncInfo,
            messages=[{"role": "system", "content": SYS_PROMPT}, {"role": "user", "content": user_input}],
        )
    elif USE_ANTHROPIC:
        func_info = client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": user_input,
                }
            ],
            model= ANTHROPIC_MODEL,
            response_model = FuncInfo
        )
    elif USE_OPENROUTER_API:
        func_info = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            response_model=FuncInfo,
            messages=[
                {"role": "system", "content": SYS_PROMPT},
                {"role": "user", "content": user_input}
            ],
        )
    return func_info

def call_llm(user_input: str, sys_prompt: str = "", ai_input: str = "") -> str:
    if llm is None:
        raise Exception("No OpenAI client found. Please set USE_OPENAI_API, USE_ANTHROPIC or USE_AZURE_OPENAI_API environment variable to True")
    try:
        if USE_OPENAI_API:
            response = llm.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0,
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_input}, {"role": "assistant", "content": ai_input}],
            )
            return response.choices[0].message.content
        elif USE_AZURE_OPENAI_API:
            response = llm.chat.completions.create(
                model= AZURE_OPENAI_API_DEPLOYMENT_NAME,
                temperature=0,
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_input}, {"role": "assistant", "content": ai_input}],
            )
            return response.choices[0].message.content
        elif USE_ANTHROPIC:
            response = llm.messages.create(
                max_tokens=1024,
                system= sys_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ],
                model= ANTHROPIC_MODEL
            )
            logger.info(f"call_llm USE_ANTHROPIC response: {response.content}")
            return response.content
        elif USE_OPENROUTER_API:
            response = llm.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_input,},
                {"role": "assistant", "content": ai_input},
            ],
            )
            return response.choices[0].message.content
    except Exception as e:
        logger.error(f"call_llm Error: {e}")
        return "Error: Unable to connect to the model."



if __name__ == "__main__":
    user_input = "Implement a python function that can write a string to a file"
    print(call_llm(user_input))
    # print(generate_func(user_input))