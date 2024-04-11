from ai_coder.ai_decorators import ai_code

@ai_code
def add(a, b):
    f"Implement an add function that takes two numbers and returns their sum."


def sub(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    return a / b


def calculate(operation, num1, num2):
    if operation == 'add':
        return add(num1, num2)
    elif operation == 'sub':
        return sub(num1, num2)
    elif operation == 'multiply':
        return multiply(num1, num2)
    elif operation == 'divide':
        return divide(num1, num2)
    else:
        raise ValueError('Operation not supported')


if __name__ == "__main__":
    while True:
        print('Enter operation (add, sub, multiply, divide):', end=' ')
        operation = input()
        num1 = float(input('Enter first number: '))
        num2 = float(input('Enter second number: '))
        result = calculate(operation, num1, num2)
        print(f'{num1} {operation} {num2} = {result}')
        print()
