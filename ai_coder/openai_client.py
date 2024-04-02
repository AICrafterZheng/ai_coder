import os
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from ai_coder.prompts import SYS_PROMPT
from loguru import logger

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
    model = ChatOpenAI(model=OPENAI_MODEL)
    if AZURE_OPENAI_API_KEY != "":
        logger.info(f"Using Azure OpenAI API, version: {AZURE_OPENAI_API_VERSION}, model: {AZURE_OPENAI_API_DEPLOYMENT_NAME}")
        os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
        os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_API_BASE
        model = AzureChatOpenAI(
            openai_api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_API_DEPLOYMENT_NAME,
        )
except Exception as e:
    logger.error(f"Model Error: {e}")

def call_llm(user_input: str, sys_prompt: str = "", ai_input: str = "") -> str:
    try:
        system_message = SystemMessage(content=sys_prompt)
        human_message = HumanMessage(content=user_input)
        ai_message = AIMessage(content=ai_input)
        # logger.debug(f"system_message: {system_message.content}\nuser_input: {human_message.content}\nai_input: {ai_message.content}")
        response = model.invoke([system_message, human_message, ai_message])
        return response.content
    except Exception as e:
        logger.error(f"call_llm Error: {e}")
        return "Error: Unable to connect to the model."


if __name__ == "__main__":
    response = call_llm("Implement a function that takes a string and returns the first character that appears only once in the string.")
    logger.info(response)