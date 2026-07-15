from langchain_ollama import ChatOllama

from config import MODEL_NAME
from validator import validate_python_syntax
from services import generate_fix, retry_fix, execute_code


llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)


def review_code(code: str):
    """
    Main workflow of the Self-Correcting Code Agent.
    """

    # Step 1: Validate syntax
    syntax_result = validate_python_syntax(code)

    if not syntax_result["valid"]:
        return {
            "success": False,
            "message": "Syntax Error Detected",
            "error": syntax_result["error"]
        }

    history = []

    # Step 2: Generate corrected code
    fixed_code = generate_fix(llm, code)

    # Step 3: Execute corrected code
    execution_result = execute_code(fixed_code)

    history.append({
        "attempt": 1,
        "code": fixed_code,
        "success": execution_result["success"],
        "stdout": execution_result["stdout"],
        "stderr": execution_result["stderr"]
    })

    max_retries = 3
    retry = 0

    # Step 4: Retry if execution fails
    while not execution_result["success"] and retry < max_retries:

        fixed_code = retry_fix(
            llm,
            fixed_code,
            execution_result["stderr"]
        )

        execution_result = execute_code(fixed_code)

        history.append({
            "attempt": retry + 2,
            "code": fixed_code,
            "success": execution_result["success"],
            "stdout": execution_result["stdout"],
            "stderr": execution_result["stderr"]
        })

        retry += 1

    # Step 5: Return final response
    return {
        "success": execution_result["success"],
        "final_code": fixed_code,
        "execution_result": execution_result,
        "retries": retry,
        "history": history
    }