from ai_coder.ai_decorators import ai_code

@ai_code
def get_top_hacker_news():
    return """Implement a function that can fetch the top hacker news, which mention certain keywords, e.g. 'gpt', 'llm', 'workflow', 'serverless'.
    You can use the url \"https://hacker-news.firebaseio.com/v0/topstories.json\" to fetch the top hacker news. 
    Please only return the story title and the url.
    The input is the keywords and the output is a list of the news."""