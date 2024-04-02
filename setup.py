from setuptools import setup, find_packages
setup(
    name='ai_coder',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ai_coder = ai_coder.cli:main',  # This line creates a command named 'ai_coder' that calls the 'main' function in the 'cli' module
        ],
    },
    install_requires=[
        "langchain",
        "langchain-openai",
        "python-dotenv",
        "astor",
        "loguru",
        "black",
        "ruff"
    ],
)
