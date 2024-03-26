###This file is generated by AI from examples/tech_crunch_ai_news/prompts/src/main.py. DO NOT MODIFY THIS FILE MANUALLY###

import requests
from bs4 import BeautifulSoup
from ai_coder.openai_client import call_llm

def article_summary(url: str) ->str:
    """
    Function to fetch a webpage and get its summary using call_llm function
    :param url: string, url of the webpage
    :return: string, summary of the webpage
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    webpage_text = soup.get_text()
    summary = call_llm(webpage_text, 'Please summarize this text')
    return summary