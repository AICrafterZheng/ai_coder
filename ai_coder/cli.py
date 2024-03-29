import ast
import astor
from ai_coder.openai_client import call_llm
import argparse
import os
from ai_coder.file_utils import read_file, write_file
from ai_coder.prompts import SYS_PROMPT, CLEANUP_PROMPT
import importlib
import inspect
from loguru import logger
from typing import List, Union

class AICoder:
    def __init__(self) -> None:
        self.tree = None

    def gen_code(self, filePath: str) -> None:
        # Write the new code to a file
        directories = filePath.split(os.sep)
        out_dir = f"./{os.sep.join(directories[1:len(directories)-1])}"
        logger.info(f"out_dir: {out_dir}")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        out_path = f"./{os.sep.join(directories[1:])}"
        logger.info(f"Generating code from {filePath} to {out_path}...")
        existing_tree = None
        if os.path.exists(out_path):
            existing_code = read_file(out_path)
            if existing_code.strip() != "":
                existing_tree = ast.parse(existing_code)

        code = read_file(filePath)
        self.tree = ast.parse(code)

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and hasattr(node, 'decorator_list'):
                decorators = [d.id for d in node.decorator_list]
                if 'ai_code' in decorators:
                    if self.is_force_update(node):
                        new_body = self.get_function_implementation(node)
                        self.replace_function_implementation(node, node.name, new_body)
                        logger.info(f"Saving the generated code to {out_path}.")
                    elif self.is_function_prompt_updated(node):
                        new_body = self.get_function_implementation(node)
                        self.replace_function_implementation(node, node.name, new_body)
                        logger.info(f"Saving the generated code to {out_path}.")
                    elif existing_tree and self.is_function_defined(node.name):
                        new_body = self.get_function_from_tree(existing_tree, node.name).body
                        self.replace_function_implementation(node, node.name, new_body)
                    else:
                        new_body = self.get_function_implementation(node)
                        self.replace_function_implementation(node, node.name, new_body)
                        logger.info(f"Saving the generated code to {out_path}.")

        save_code = astor.to_source(self.tree)
        write_file(out_path, save_code)

        full_code = read_file(out_path)
        logger.info("Reviewing the code...")
        full_code = call_llm(full_code, CLEANUP_PROMPT.format(filePath))
        write_file(out_path, full_code)
        logger.info("Finished generating the code!")


    def is_force_update(self, function: ast.FunctionDef) -> bool:
        return False #TODO

    def is_function_prompt_updated(self, function: ast.FunctionDef) -> bool:
        return False #TODO

    def is_function_defined(self, function: str) -> bool:
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == function:
                return True
        return False

    def get_function_from_tree(self, tree: ast.AST, function_name: str) -> Union[ast.FunctionDef, None]:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return node
        return None

    def get_function_f_string_info(self, function_def: ast.FunctionDef) -> Union[str, None]:
        # Find the f-string node within the function body
        f_string_node = None
        for node in ast.walk(function_def):
            if isinstance(node, ast.JoinedStr):
                f_string_node = node
                break
        if f_string_node:
            # Get the f-string
            f_string = ast.unparse(f_string_node)
            # Find the formatted values in the f-string
            formatted_values = []
            for value in f_string_node.values:
                if isinstance(value, ast.FormattedValue):
                    formatted_values.append(ast.unparse(value.value))

            # Check if any formatted value is a global variable or function and get its information for LLM to use
            for value in formatted_values:
                try:
                    if self.is_variable_defined(value):
                        f_string += f"\n The variable: {value} is already defined, you can just use it."
                    else:
                        signature = self.get_function_signature(value)
                        f_string += signature
                except NameError as e:
                    logger.error(f"Function '{value}' error: {e}")
            return f_string
        else:
            logger.warning("F-string not found in the function.")
            return None

    def get_function_signature(self, function_name: str) -> str:
        # Find the import statement for call_llm
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == function_name:
                        logger.info(f"Function {function_name} is imported. Checking the signature...")
                        # Import the module containing the function
                        module_name = node.module
                        module = importlib.import_module(module_name)
                        # Get the imported function
                        imported_function = getattr(module, alias.name)
                        # Get the function signature
                        signature = inspect.signature(imported_function)
                        return f" The function {function_name} is imported, and has signature {signature}. You can just call it."
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                logger.info(f"Function {function_name} is defined. Checking the signature...")
                # Get the function arguments
                args = [arg.arg for arg in node.args.args]
                # Get the function return type
                if isinstance(node.returns, ast.Name):
                    return_type = node.returns.id
                elif isinstance(node.returns, ast.Constant):
                    return_type = node.returns.value
                else:
                    return_type = None
                return f" The function {function_name} is defined, and has signature ({', '.join(args)}) -> {return_type}. You can just call it."
        return ""

    def is_variable_defined(self, variable_name: str) -> bool:
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == variable_name:
                        return True
        return False

    def get_prompt(self, function_def: ast.FunctionDef) -> str:
        # Get the function docstring
        docstring = ast.get_docstring(function_def)
        if docstring:
            return docstring
        f_string = self.get_function_f_string_info(function_def)
        if f_string:
            return f_string
        # Get the function constants
        constants = []
        for node in ast.walk(function_def):
            if isinstance(node, ast.Constant):
                constants.append(node.value)
        return " ".join(constants)

    def get_function_implementation(self, node: ast.FunctionDef) -> List[ast.AST]:
        # Extract the description from the return statement
        prompt = self.get_prompt(node)
        logger.info(f"The prompt to generate the code for function {node.name}: {prompt}")
        generated_code = call_llm(prompt, sys_prompt=SYS_PROMPT)
        logger.info(f"generated_code: {generated_code}")
        # Replace the function body with the generated code
        generated_code = generated_code.replace("```python", "").replace("```", "")
        new_body = ast.parse(generated_code).body
        logger.info(f"new body: {new_body}")
        return new_body

    def replace_function_implementation(self, tree: ast.AST, function_name: str, new_body: List[ast.AST]) -> ast.AST:
        class ReplaceFunction(ast.NodeTransformer):
            def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
                if node.name == function_name:
                    # Replace the function body
                    node.body = new_body
                    # Fix missing locations in the new function body
                    ast.fix_missing_locations(node)
                return node
        transformer = ReplaceFunction()
        new_tree_list = transformer.visit(tree)
        return new_tree_list

def main() -> None:
    # Create the parser
    parser = argparse.ArgumentParser(description='AI Coder Tool')
    subparsers = parser.add_subparsers(dest='command')

    # Subcommand: gen_code
    parser_gen_code = subparsers.add_parser('gen', help='Generate code from a file')
    parser_gen_code.add_argument('filepath', type=str, help='The file to generate code from')

    args = parser.parse_args()
    logger.info(f"args: {args}")
    if args.command == 'gen':
        ai_coder = AICoder()
        ai_coder.gen_code(args.filepath)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()