from langchain_ollama import ChatOllama
from analyzer import analyze_code
from config import MODEL_NAME
from validator import validate_python_syntax

from services import (
    retry_fix,
    execute_code,
    create_tests,
    run_tests
)


llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)


def determine_failure_type(
    execution_result,
    test_result
):
    """
    Determine what kind of failure occurred.
    """

    # Execution timeout
    if execution_result.get("timeout", False):
        return "TIMEOUT"

    # Runtime error
    if not execution_result["success"]:
        return "RUNTIME_ERROR"

    # Test timeout
    if test_result.get("timeout", False):
        return "TEST_TIMEOUT"

    # Generated test failure
    if not test_result["success"]:
        return "TEST_FAILURE"

    return "SUCCESS"


def review_code(code: str, description: str = ""):
    """
    Main workflow of the Self-Correcting Code Agent.

    Workflow:

    1. Validate original syntax
    2. Generate tests using code + specification
    3. Execute original code
    4. Run generated tests
    5. Determine failure type
    6. Ask the LLM to fix the code
    7. Execute corrected code
    8. Run the same tests
    9. Repeat until tests pass or retry limit is reached
    """

    # STEP 1: Validate original syntax

    syntax_result = validate_python_syntax(code)

    if not syntax_result["valid"]:

        return {
            "success": False,
            "message": "Syntax Error Detected",
            "error": syntax_result["error"],
            "original_code": code,
            "final_code": code,
            "retries": 0,
            "history": []
        }
    analysis_result = analyze_code(code)

    # STEP 2: Generate tests

    tests = create_tests(
        code,
        description
    )

    # STEP 3: Execute original code

    execution_result = execute_code(code)

    # STEP 4: Run tests

    if execution_result["success"]:

        test_result = run_tests(
            code,
            tests
        )

    else:

        test_result = {
            "success": False,
            "stdout": execution_result["stdout"],
            "stderr": execution_result["stderr"],
            "timeout": execution_result.get(
                "timeout",
                False
            )
        }

    # STEP 5: Determine failure

    failure_type = determine_failure_type(
        execution_result,
        test_result
    )

    # STEP 6: Record initial attempt

    history = [
        {
            "attempt": 1,
            "code": code,
            "tests": tests,

            "failure_type": failure_type,

            "execution_success":
                execution_result["success"],

            "execution_stdout":
                execution_result["stdout"],

            "execution_stderr":
                execution_result["stderr"],

            "test_success":
                test_result["success"],

            "test_stdout":
                test_result["stdout"],

            "test_stderr":
                test_result["stderr"]
        }
    ]

    # STEP 7: Self-correction loop

    max_retries = 3
    retry = 0

    current_code = code

    while (
        not test_result["success"]
        and retry < max_retries
    ):

        # Determine the most relevant error

        if execution_result.get("timeout", False):

            error = execution_result["stderr"]

        elif not execution_result["success"]:

            error = execution_result["stderr"]

        else:

            error = test_result["stderr"]

        # Determine failure type again

        failure_type = determine_failure_type(
            execution_result,
            test_result
        )

        # Ask LLM to correct the implementation

        current_code = retry_fix(
            llm,
            current_code,
            tests,
            error,
            failure_type,
            description,
            analysis_result
        )
        analysis_result = analyze_code(
            current_code
        )

        retry += 1

        # Validate corrected code

        syntax_result = validate_python_syntax(
            current_code
        )

        if not syntax_result["valid"]:

            execution_result = {
                "success": False,
                "stdout": "",
                "stderr": syntax_result["error"],
                "timeout": False
            }

            test_result = {
                "success": False,
                "stdout": "",
                "stderr": syntax_result["error"],
                "timeout": False
            }

            failure_type = "SYNTAX_ERROR"

            history.append(
                {
                    "attempt": retry + 1,
                    "code": current_code,
                    "tests": tests,

                    "failure_type":
                        failure_type,

                    "execution_success": False,
                    "execution_stdout": "",
                    "execution_stderr":
                        syntax_result["error"],

                    "test_success": False,
                    "test_stdout": "",
                    "test_stderr":
                        syntax_result["error"]
                }
            )

            continue

        # Execute corrected code

        execution_result = execute_code(
            current_code
        )

        # Run tests only if execution succeeds

        if execution_result["success"]:

            test_result = run_tests(
                current_code,
                tests
            )

        else:

            test_result = {
                "success": False,
                "stdout":
                    execution_result["stdout"],
                "stderr":
                    execution_result["stderr"],
                "timeout":
                    execution_result.get(
                        "timeout",
                        False
                    )
            }

        # Determine new failure type

        failure_type = determine_failure_type(
            execution_result,
            test_result
        )

        # Store attempt

        history.append(
            {
                "attempt": retry + 1,
                "code": current_code,
                "tests": tests,

                "failure_type":
                    failure_type,

                "execution_success":
                    execution_result["success"],

                "execution_stdout":
                    execution_result["stdout"],

                "execution_stderr":
                    execution_result["stderr"],

                "test_success":
                    test_result["success"],

                "test_stdout":
                    test_result["stdout"],

                "test_stderr":
                    test_result["stderr"]
            }
        )

    # STEP 8: Final response

    if test_result["success"]:

        message = "Code passed generated tests"

    else:

        message = (
            "Code failed generated tests "
            "after retries"
        )

    return {
        "success":
            test_result["success"],

        "message":
            message,

        "original_code":
            code,

        "description":
            description,

        "final_code":
            current_code,

        "tests":
            tests,

        "analysis": 
            analysis_result,

        "execution_result":
            execution_result,

        "test_result":
            test_result,

        "retries":
            retry,

        "history":
            history
    }