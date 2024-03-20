# ai_coder

## Developing and Contributing
From the root of this repo:

Create a virtual env and activate.
``` bash
python3 -m venv .venv
```
>How you activate the environment depends on your operating system and shell. Typically, it involves sourcing an **`activate`** script located in the virtual environment's **`bin`** (Unix-based) or **`Scripts`** (Windows) directory.

For Unix-based systems:

```bash
. ./.venv/bin/activate
```

For Windows Command Prompt:
```
.\.venv\Scripts\activate

```

Install ai_coder into your pip environment with:
``` bash
pip install -e .
```
This installs the ai_coder package in editable mode. All imports of ai_coder will run the ai_coder source at `./ai_coder` directly.

### Use ai_coder in another project (Let's see Project B)
#### **Step 1: Identify the Path to ai_coder**

First, you need to find the absolute path to ai_coder's directory. This is the directory that contains the **`setup.py`** file. You can navigate to this directory in your terminal and use a command to get the path:
- On Unix-based systems (Linux, macOS), you can use **`pwd`**.
- On Windows, you can use **`cd`** without arguments or **`echo %cd%`** in Command Prompt (or **`echo $PWD`** in PowerShell).
#### **Step 2: Activate Project B's Virtual Environment**

Before you install ai_coder as a dependency in Project B, make sure Project B's virtual environment is activated.

#### **Step 3: Install ai_coder in Editable Mode into Project B's Environment**

With Project B's virtual environment activated, use **`pip`** to install ai_coder in editable mode using the path you obtained in Step 1. Replace **`/path/to/projectA`** with the actual path to ai_coder:

```bash
pip install -e /path/to/ai_coder
```

This command will install ai_coder into Project B's virtual environment in editable mode. Any changes made to ai_coder's code will be reflected in Project B without needing to reinstall ai_coder.


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
ai_coder gen prompts/src/my_code.py

```

