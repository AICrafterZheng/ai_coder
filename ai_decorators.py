from ai_coder.openai_client import callLLM
from ai_coder.file_utils import write_file, append_file, read_file
from typing import Optional
import os
class ai_code:
    def __init__(self, function = None, filename: Optional[str] = None):
        self.filename = filename
        self.function = function
        if function is not None:
            self.__call__(function)
    def __call__(self, function):
        task = function()
        print(f"task: {task}")
        task += f". please use the function name {function.__name__} to implement the function."
        res = callLLM(task)
        print(f"code:\n {res}")
        if self.filename is None:
            self.filename = f"{function.__name__}"
        dir = "generated"
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        filePath = f"{dir}/{self.filename}.py"
        if os.path.exists(filePath):
            append_file(filePath, f"\n\n{res}")
            code = read_file(filePath)
            code = callLLM(code, "Please move the imports to the top of the file. And remove the duplicate imports. And remove the duplicate functions.")
            write_file(filePath, code)
        else:
            write_file(filePath, res)        
