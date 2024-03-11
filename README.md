# ai_coder

## Developing and Contributing
From the root of this repo:

Create a virtual env
``` bash
python3 -m venv venv
. ./venv/bin/activate
```

Install ai_coder into your pip environment with:
``` bash
pip install -e .
```
This installs the ai_coder package in editable mode. All imports of ai_coder will run the ai_coder source at `./ai_coder` directly.

## Test
### 1. Setup OPENAI API KEY
It currently executes the prompt with OpenAI, so you'll need to use your own OpenAI API Key
``` bash
export OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz
```

### 2. Add below code to `prompts/src/my_code.py`
```
from ai_coder.ai_decorators import ai_code

@ai_code
def get_top_hacker_news():
    return """Implement a function that can fetch the top hacker news, which mention certain keywords, e.g. 'gpt', 'llm', 'workflow', 'serverless'.
    You can use the url \"https://hacker-news.firebaseio.com/v0/topstories.json\" to fetch the top hacker news. 
    Please only return the story title and the url.
    The input is the keywords and the output is a list of the news."""
```
### 3. Run
```
ai_coder gen_code prompts/src/my_code.py

```

