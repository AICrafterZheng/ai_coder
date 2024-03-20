import ast
import astor
from ai_coder.openai_client import call_llm
import argparse
import os
from ai_coder.file_utils import read_file, write_file
from ai_coder.prompts import CLEANUP_PROMPT

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='AI Coder Tool')
    subparsers = parser.add_subparsers(dest='command')

    # Subcommand: gen_code
    parser_gen_code = subparsers.add_parser('gen', help='Generate code from a file')
    parser_gen_code.add_argument('filepath', type=str, help='The file to generate code from')

    args = parser.parse_args()
    print(f"args: {args}")
    if args.command == 'gen':
        gen_code(args.filepath)
    else:
        parser.print_help()

def gen_code(filePath):
    # Write the new code to a file
    directories = filePath.split(os.sep)
    out_dir = f"./{os.sep.join(directories[1:len(directories)-1])}"
    print(f"out_dir: {out_dir}")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    out_path = f"./{os.sep.join(directories[1:])}"
    print(f"Generating code from {filePath} to {out_path}...")
    existing_tree = None
    existing_tree_list = []
    if os.path.exists(out_path):
        existing_code = read_file(out_path)
        if existing_code.strip() != "":
            existing_tree = ast.parse(existing_code)


    code = read_file(filePath)
    tree = ast.parse(code)
    new_tree_list = []
    imports_and_assigns = []

    for node in tree.body:
        # Extract the imports and assigns
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign)):
            imports_and_assigns.append(node)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            ai_code_decorator_update = False
            has_ai_code_decorator = False
            function_name = node.name
            function_args = [arg.arg for arg in node.args.args]
            print(f"Arguments of the function {function_name}: {function_args}")
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
                    print(f"Arguments of the ai_code decorator: {args}")
                    print(f"Keyword arguments of the ai_code decorator: {kwargs}")
                    ai_code_decorator_update = kwargs.get('update', True)
                    break
            if ai_code_decorator_update:
                # Extract the description from the return statement
                if node.body and isinstance(node.body[0], ast.Return):
                    description = node.body[0].value.s
                    # Generate code for this function
                    if function_args and len(function_args) > 0:
                        description += f" \n The arguments of the function are: {function_args}."
                    generated_code = call_llm(description)
                    print(f"generated_code: {generated_code}")
                    # Replace the function body with the generated code
                    generated_code = generated_code.replace("```python", "").replace("```", "")
                    new_body = ast.parse(generated_code).body
                    node.body = new_body
                    if existing_tree is not None:
                        existing_tree = replace_function_implementation(existing_tree, function_name, new_body)
            if has_ai_code_decorator is False and existing_tree is not None:
                print(f"The function {function_name} does not have the ai_code decorator. Adding the function to the existing code.")
                existing_tree = replace_function_implementation(existing_tree, function_name, node.body)
             # Add the processed function to the list
            new_tree_list.append(node)
    
    existing_tree_list = imports_and_assigns + existing_tree.body if existing_tree is not None else []

    if existing_tree is not None:
        save_code = existing_tree_list
        print(f"Saving the updated code to {out_path}.")
    else:
        save_code = new_tree_list
        print(f"Saving the generated code to {out_path}.")

    # Create a new module with the processed functions
    new_module = ast.Module(body=save_code, type_ignores=[])
    save_code = astor.to_source(new_module)
    write_file(out_path, save_code)

    full_code = read_file(out_path)
    print("Reviewing the code...")
    full_code = call_llm(full_code, CLEANUP_PROMPT.format(filePath))
    write_file(out_path, full_code)
    print("Finished generating the code!")


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

if __name__ == "__main__":
    main()

