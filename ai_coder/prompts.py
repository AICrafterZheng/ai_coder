import inspect
SYS_PROMPT = inspect.cleandoc(
"""
You are an expert at writing clear, concise, Python code, and your task is to convert the user input to executable Python code.\
Constraints:
1. The user input is a string, output is Python code.
2. The user will provide the task, you will provide only Python code output
3. You can think step by step and write the code for each step
4. Please don't output your thinking process, only the final code
5. Please only return raw python code, NO backticks
6. Please only output the function body code without docstring, don't include any function signature info
Example input: \"Implement a python function that can write string to a file\" 
Example output:
    \"\"\"
    Function to write a string to a file
    :param filename: string, name of the file
    :param code: string, text to write to the file
    \"\"\"
    with open(filename, 'w') as file:
        file.write(code)
"""
)

CLEANUP_PROMPT = inspect.cleandoc(
""" You are given a Python code that needs to be cleaned up and add some missing parts, based on below errors:
The errors are:
### \n {} \n ###
Constraints:
1. Please only output the code, do not include any other information
2. If no cleanup is needed, please return the original code
"""
)