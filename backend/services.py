from prompts import CODE_REVIEW_PROMPT, RETRY_PROMPT
from parser import extract_python_code
from tools import execute_python, execute_tests
from test_generator import generate_tests


def generate_fix(llm, code):
    """
    Ask the LLM to review and correct the supplied code.
    """

    prompt = CODE_REVIEW_PROMPT.format(
        code=code
    )

    response = llm.invoke(prompt).content

    fixed_code = extract_python_code(response)

    return fixed_code


def retry_fix(
    llm,
    code,
    tests,
    error,
    failure_type,
    description,
    analysis
):
    """
    Ask the LLM to fix code using:

    - current code
    - original specification
    - generated tests
    - failure information
    - failure type
    - static analysis
    """

    prompt = RETRY_PROMPT.format(
        code=code,
        description=description,
        tests=tests,
        error=error,
        failure_type=failure_type,
        analysis=analysis
    )

    response = llm.invoke(prompt).content

    fixed_code = extract_python_code(response)

    return fixed_code


def execute_code(code):
    """
    Execute Python code.
    """

    return execute_python(code)


def create_tests(code, description=""):
    """
    Generate tests using the supplied code
    and problem specification.
    """

    return generate_tests(
        code,
        description
    )


def run_tests(code, tests):
    """
    Execute generated tests against the supplied code.
    """

    return execute_tests(
        code,
        tests
    )