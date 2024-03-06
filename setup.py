from setuptools import setup, find_packages

setup(
    name='ai_coder',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ai_coder = cli:main',  # This line creates a command named 'aicoder' that calls the 'main' function in the 'cli' module
        ],
    },
)
