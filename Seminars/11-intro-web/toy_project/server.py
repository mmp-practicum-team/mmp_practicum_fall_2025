from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from longest_palindrome import find_palindrome

app = FastAPI()

@app.get("/longest-palindrome/{input_string}", response_class=PlainTextResponse)
def longest_palindrome(input_string: str):
    return find_palindrome(input_string)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)