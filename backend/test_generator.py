from langchain_ollama import ChatOllama

from config import MODEL_NAME
from parser import extract_python_tests


llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)


TEST_GENERATION_PROMPT = """
You are an expert Python test engineer.

Generate a small, diverse set of executable Python assertions
for the supplied program.

SPECIFICATION:

{description}


CODE:

{code}


TEST DESIGN REQUIREMENTS:

1. Generate approximately 5 to 8 tests.
2. Do NOT generate more than 8 tests.
3. Every test must start with `assert`.
4. Test normal behavior.
5. Test edge cases.
6. Test boundary cases when applicable.
7. Test negative values when applicable.
8. Test empty inputs when applicable.
9. Test single-element inputs when applicable.
10. Avoid duplicate tests.
11. Prefer tests that exercise different branches.
12. Use the specification as the primary source of expected behavior.
13. Carefully calculate every expected result.
14. Verify arithmetic before returning the result.
15. Do not guess expected values.
16. Do not create intentionally failing tests.
17. The expected value in every assertion must represent the
    correct behavior described by the specification.

IMPORTANT:

For numerical problems, manually verify each expected value.

For example:

maximum([-10, -20, -30, -40, -50]) == -10

NOT:

maximum([-10, -20, -30, -40, -50]) == -50

STRICT OUTPUT RULES:

1. Return ONLY Python assert statements.
2. DO NOT create functions.
3. DO NOT use `def`.
4. DO NOT use pytest.
5. DO NOT use unittest.
6. DO NOT create classes.
7. DO NOT include a filename.
8. DO NOT include explanations.
9. DO NOT include markdown.
10. DO NOT use ``` blocks.
11. DO NOT redefine the original functions.
12. The output must be directly executable after the original code.

Return ONLY the assertions.
"""


def generate_tests(code: str, description: str = ""):
    """
    Generate a small, diverse assertion-based test suite.
    """

    if not description.strip():
        description = (
            "Infer the expected behavior from the supplied "
            "Python code."
        )

    prompt = TEST_GENERATION_PROMPT.format(
        code=code,
        description=description
    )

    response = llm.invoke(prompt).content

    tests = extract_python_tests(response)

    return tests