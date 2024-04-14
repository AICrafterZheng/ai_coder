import re
import subprocess
import ast
import astor
from ai_coder.file_utils import read_file, write_file
from ai_coder.logger import logger
from ai_coder.llm_client import call_llm
from ai_coder.prompts import CLEANUP_PROMPT

def run_pylint(file_path):
    """Run pylint on the specified file."""
    result = subprocess.run(['pylint', file_path], capture_output=True, text=True)
    logger.info(f"run_pylint: {result}")
    return result.stdout

def run_ruff(file_path):
    """Run ruff on the specified file."""
    result = subprocess.run(['ruff', 'check', file_path, '--fix'], capture_output=True, text=True)
    logger.info(f"run_ruff: {result.stdout}")
    return result.stdout

def run_black(file_path):
    """Run black on the specified file."""
    result = subprocess.run(['black', file_path], capture_output=True, text=True)
    logger.info(f"run_black: {result}")
    return result

def remove_decorator(tree: ast.AST) -> ast.AST:
    # Create a transformer to remove the @ai_code decorator
    class AiCodeDecoratorRemover(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.decorator_list = [n for n in node.decorator_list if not isinstance(n, ast.Name) or n.id != 'ai_code']
            return node

    # Apply the transformer to the AST
    transformer = AiCodeDecoratorRemover()
    modified_tree = transformer.visit(tree)
    return modified_tree

def move_imports_to_top(tree: ast.AST) -> ast.AST:
    # Create a transformer to move imports to the top
    class ImportMover(ast.NodeTransformer):
        def __init__(self):
            self.imports = []

        def visit_FunctionDef(self, node):
            # Collect import statements inside the function
            self.imports = [n for n in node.body if isinstance(n, ast.Import) or isinstance(n, ast.ImportFrom)]
            # Remove import statements from the function body
            node.body = [n for n in node.body if not isinstance(n, ast.Import) and not isinstance(n, ast.ImportFrom)]
            return node

        def move_imports(self, node):
            # Insert the collected imports at the top of the module
            node.body = self.imports + node.body
            return node

    # Apply the transformer to the AST
    transformer = ImportMover()
    modified_tree = transformer.visit(tree)
    modified_tree = transformer.move_imports(modified_tree)
    return modified_tree


def format_code(file_path: str) -> str:
    code = read_file(file_path)
    # Parse the code into an AST
    tree = ast.parse(code)
    modified_tree = move_imports_to_top(tree)
    modified_tree = remove_decorator(modified_tree)
    # # Convert the modified AST back to source code
    modified_code = astor.to_source(modified_tree)
    # Write the formatted code back to the file
    write_file(file_path, modified_code)
    run_black(file_path)
    return run_ruff(file_path)

def review_code(filePath: str) -> None:
    logger.info("Reviewing the code...")
    error = format_code(filePath)
    if "F821" in error: #Fixing Error like: F821 Undefined name `requests`
        logger.info("Error detected in the code. Fixing the code...")
        save_code = read_file(filePath)
        save_code = call_llm(save_code, sys_prompt=CLEANUP_PROMPT.format(error), ai_input="The code is")
        save_code = extract_code(save_code)
        logger.info("Formatting the code again after fixing the error...")
        write_file(filePath, save_code)
        format_code(filePath)

def extract_code(text: str) -> str:
    pattern = r'```python\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        logger.info("Extracted code from ```python")
        code_block = match.group(1)
        return code_block
    else:
        logger.info("No ```python, do nothing, return the original text.")
        return text

if __name__ == '__main__':
    file_path = 'tmp1.py'
    code = read_file(file_path)
    logger.info(extract_code(code))

