from prompts import CODE_REVIEW_PROMPT, RETRY_PROMPT
from parser import extract_python_code
from tools import execute_python


def generate_fix(llm, code):

    prompt = CODE_REVIEW_PROMPT.format(code=code)

    response = llm.invoke(prompt).content

    fixed_code = extract_python_code(response)

    return fixed_code


def retry_fix(llm, code, error):

    prompt = RETRY_PROMPT.format(
        code=code,
        error=error
    )

    response = llm.invoke(prompt).content

    fixed_code = extract_python_code(response)

    return fixed_code


def execute_code(code):

    return execute_python(code)