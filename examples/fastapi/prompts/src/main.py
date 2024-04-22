from ai_coder.ai_decorators import ai_code
from fastapi import FastAPI
app = FastAPI()

@ai_code
@app.post("/add/")
def add(item: Item) -> float:
    """Implement a POST API to add two numbers a and b using FastAPI"""

@ai_code
@app.post("/sub/")
def sub(item: Item) -> float:
    """Implement a POST API to subtract two numbers a and b using FastAPI"""

@ai_code
@app.post("/multiply/")
def multiply(item: Item) -> float:
    """Implement a POST API to multiply two numbers a and b using FastAPI"""

@ai_code
@app.post("/divide/")
def divide(item: Item) -> float:
    """Implement a POST API to divide two numbers a and b using FastAPI"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
