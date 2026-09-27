from pydantic import BaseModel


class CodeRequest(BaseModel):
    code: str
    description: str = ""