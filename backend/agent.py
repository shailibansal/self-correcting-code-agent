from langchain_ollama import ChatOllama
from config import MODEL_NAME
from prompts import CODE_REVIEW_PROMPT, RETRY_PROMPT
from tools import execute_python
from parser import extract_python_code

llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)


def review_code(code: str):

    history = []

    prompt = CODE_REVIEW_PROMPT.format(code=code)

    response = llm.invoke(prompt).content

    fixed_code = extract_python_code(response)

    execution_result = execute_python(fixed_code)

    history.append({
    "attempt": retry + 2,
    "code": fixed_code,
    "success": execution_result["success"],
    "stdout": execution_result["stdout"],
    "stderr": execution_result["stderr"]
    })

    max_retries = 3
    retry = 0

    while not execution_result["success"] and retry < max_retries:

        retry_prompt = RETRY_PROMPT.format(
            code=fixed_code,
            error=execution_result["stderr"]
        )

        response = llm.invoke(retry_prompt).content

        fixed_code = extract_python_code(response)

        execution_result = execute_python(fixed_code)

        retry += 1

    return {
    "final_code": fixed_code,
    "execution_result": execution_result,
    "retries": retry,
    "history": history
    }