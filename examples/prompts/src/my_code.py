from ai_coder.ai_decorators import ai_code

@ai_code
def get_top_hacker_news():
    return """Implement a function that can fetch the top hacker news, which mention certain keywords, e.g. 'gpt', 'llm', 'workflow', 'serverless'.
    You can use the url \"https://hacker-news.firebaseio.com/v0/topstories.json\" to fetch the top hacker news. 
    Please only return the story title and the url.
    The input is the keywords and the output is a list of the news."""

@ai_code
def article_summary():
    return """Implement a function that can fetch a webpage and  call `callLLM` (import callLLM from ai_coder.openai_client) to get the summary of the webpage. 
    The callLLM function takes two arguments, the first argument is the text to summarize and the second argument is the task to perform.
    The input is the url of the webpage and the output is the summary of the webpage."""