import ast
import astor
from ai_coder.openai_client import call_llm
import argparse
import os
from ai_coder.file_utils import read_file, write_file
from ai_coder.prompts import CLEANUP_PROMPT
import importlib
import inspect
from loguru import logger

class AICoder:
    def __init__(self):
        self.tree = None

    def execute_imports(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    imported_module = importlib.import_module(module_name)
                    globals()[module_name] = imported_module
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module
                imported_module = importlib.import_module(module_name)
                for alias in node.names:
                    attribute_name = alias.name
                    attribute = getattr(imported_module, attribute_name)
                    globals()[attribute_name] = attribute
    
    def execute_globals(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                attr_name = node.targets[0].id
                attr_value = ast.literal_eval(node.value)
                globals()[attr_name] = attr_value

    def gen_code(self, filePath):
        # Write the new code to a file
        directories = filePath.split(os.sep)
        out_dir = f"./{os.sep.join(directories[1:len(directories)-1])}"
        logger.info(f"out_dir: {out_dir}")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        out_path = f"./{os.sep.join(directories[1:])}"
        logger.info(f"Generating code from {filePath} to {out_path}...")
        existing_tree = None
        existing_tree_list = []
        if os.path.exists(out_path):
            existing_code = read_file(out_path)
            if existing_code.strip() != "":
                existing_tree = ast.parse(existing_code)


        code = read_file(filePath)
        self.tree = ast.parse(code)
        self.execute_imports()
        self.execute_globals()

        new_tree_list = []
        imports_and_assigns = []

        for node in self.tree.body:
            # Extract the imports and assigns
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign)):
                imports_and_assigns.append(node)

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                ai_code_decorator_update = False
                has_ai_code_decorator = False
                function_name = node.name
                function_args = [arg.arg for arg in node.args.args]
                logger.info(f"Arguments of the function {function_name}: {function_args}")
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'ai_code':
                        has_ai_code_decorator = True
                        ai_code_decorator_update = True
                        node.decorator_list = []
                        break
                    elif isinstance(decorator, ast.Call) and decorator.func.id == 'ai_code':
                        has_ai_code_decorator = True
                        args = [ast.literal_eval(arg) for arg in decorator.args] if hasattr(decorator, 'args') else []
                        # Get the keyword arguments
                        kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in decorator.keywords} if hasattr(decorator, 'keywords') else {}
                        logger.info(f"Arguments of the ai_code decorator: {args}")
                        logger.info(f"Keyword arguments of the ai_code decorator: {kwargs}")
                        ai_code_decorator_update = kwargs.get('update', True)
                        break
                if ai_code_decorator_update:
                    # Extract the description from the return statement
                    prompt = self.get_promt(node)
                    logger.info(f"The Prompt to generate the code for function {function_name}: {prompt}")
                    generated_code = call_llm(prompt)
                    logger.info(f"generated_code: {generated_code}")
                    # Replace the function body with the generated code
                    generated_code = generated_code.replace("```python", "").replace("```", "")
                    new_body = ast.parse(generated_code).body
                    node.body = new_body
                    if existing_tree is not None:
                        existing_tree = self.replace_function_implementation(existing_tree, function_name, new_body)
                if has_ai_code_decorator is False and existing_tree is not None:
                    logger.info(f"The function {function_name} does not have the ai_code decorator. Adding the function to the existing code.")
                    existing_tree = self.replace_function_implementation(existing_tree, function_name, node.body)
                # Add the processed function to the list
                new_tree_list.append(node)
        
        existing_tree_list = imports_and_assigns + existing_tree.body if existing_tree is not None else []

        if existing_tree is not None:
            save_code = existing_tree_list
            logger.info(f"Saving the updated code to {out_path}.")
        else:
            save_code = new_tree_list
            logger.info(f"Saving the generated code to {out_path}.")

        # Create a new module with the processed functions
        new_module = ast.Module(body=save_code, type_ignores=[])
        save_code = astor.to_source(new_module)
        write_file(out_path, save_code)

        full_code = read_file(out_path)
        logger.info("Reviewing the code...")
        full_code = call_llm(full_code, CLEANUP_PROMPT.format(filePath))
        write_file(out_path, full_code)
        logger.info("Finished generating the code!")


    def is_function_defined(self, function):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == function:
                return True
        return False


    def get_function_f_string_info(self, function_def):
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

            # Check if any formatted value is a function and get its information
            for value in formatted_values:
                try:                    
                    if self.is_function_defined(value):
                        f_string += f"\n The function: {value} is already defined, you can just call it, which has Parameters: {self.get_func_def_param_info(value)}"
                    elif value in globals():
                        f_string += f"\n The variable: {value} is already defined, you can just use it."
                    elif inspect.isfunction(eval(value)):
                        signature = inspect.signature(eval(value))
                        parameters = signature.parameters
                        param_info = ", ".join(f"{param.name}: {param.annotation}" for param in parameters.values())
                        f_string += f"\n The function: {value} is imported, you can just call it, which has Parameters: {param_info}"
                except NameError as e:
                    logger.error(f"Function '{value}' error: {e}")
            return f_string
        else:
            logger.warning("F-string not found in the function.")
            return None
    
    def get_promt(self, function_def):
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


    def get_func_def_param_info(self, function):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == function:
                # Get the function arguments
                arguments = node.args
                arguments_list = [arg.arg for arg in arguments.args]
                return ", ".join(arguments_list)
        return ""




    def replace_function_implementation(tree, function_name, new_body):
        class ReplaceFunction(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if node.name == function_name:
                    # Replace the function body
                    node.body = new_body
                    # Fix missing locations in the new function body
                    ast.fix_missing_locations(node)
                return node
        transformer = ReplaceFunction()
        new_tree_list = transformer.visit(tree)
        return new_tree_list

def main():
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
        parser.logger.info_help()

if __name__ == "__main__":
    main()