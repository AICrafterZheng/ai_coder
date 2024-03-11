import os
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from ai_coder.prompts import SYS_PROMPT

from dotenv import load_dotenv
# Load environment variables
load_dotenv()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "")
AZURE_OPENAI_API_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_API_DEPLOYMENT_NAME", "")
AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

try:
    if OPENAI_API_KEY != "":
        print("Using OpenAI API")
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        model = ChatOpenAI(model=OPENAI_MODEL)
    else:
        print("Using Azure OpenAI API")
        os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
        os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_API_BASE
        model = AzureChatOpenAI(
            openai_api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_API_DEPLOYMENT_NAME,
        )
except Exception as e:
    print(f"Model Error: {e}")

def call_llm(user_input: str, sys_prompt: str = SYS_PROMPT):
    print(f"call_llm: {user_input}")
    try:
        system_message = SystemMessage(content=sys_prompt)
        human_message = HumanMessage(content=user_input)
        response = model([system_message, human_message])
        return response.content
    except Exception as e:
        print(f"call_llm Error: {e}")
        return "Error: Unable to connect to the model."


if __name__ == "__main__":
    response = call_llm("Implement a function that takes a string and returns the first character that appears only once in the string.")
    print(response)