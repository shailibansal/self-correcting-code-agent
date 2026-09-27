from fastapi import FastAPI

from models import CodeRequest
from agent import review_code


app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Welcome to the Self Correcting Code Agent"
    }


@app.post("/review")
def review(request: CodeRequest):

    result = review_code(
        request.code,
        request.description
    )

    return result