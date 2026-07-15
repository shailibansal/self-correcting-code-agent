from fastapi import FastAPI
from pydantic import BaseModel
from agent import review_code

app = FastAPI()


class CodeRequest(BaseModel):
    code: str


@app.get("/")
def home():
    return {"message": "Welcome to the Self Correcting Code Agent"}


@app.post("/review")
def review(request: CodeRequest):

    result = review_code(request.code)

    return result