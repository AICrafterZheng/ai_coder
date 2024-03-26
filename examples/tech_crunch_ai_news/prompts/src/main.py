from ai_coder.ai_decorators import ai_code
from ai_coder.openai_client import call_llm
@ai_code
def article_summary(url: str) -> str:
    f"""Implement a function that can fetch a webpage and  call {call_llm} to get the summary of the webpage. 
    The input is the url of the webpage and the output is the summary of the webpage."""