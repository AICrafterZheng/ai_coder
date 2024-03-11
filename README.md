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
This installs the ai_coder package in editable mode. All imports of ai_coder will run the ai_coder source at `./src/ai_coder` directly.

## run

```
ai_coder gen_code prompts/src/my_code.py

```