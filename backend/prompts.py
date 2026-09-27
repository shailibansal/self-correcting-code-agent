CODE_REVIEW_PROMPT = """
You are an expert Python developer.

Given the following Python code:

1. Find bugs.
2. Correct the code.
3. Preserve the intended functionality.
4. Return ONLY the corrected Python implementation.
5. Do NOT include tests.
6. Do NOT include assert statements.
7. Do NOT include test functions.
8. Do NOT include filenames.
9. Do not explain anything.
10. Do not use markdown.
11. Do not surround the code with ```.

Code:

{code}
"""


RETRY_PROMPT = """
You are an expert Python debugging engineer.

The following Python implementation failed during automated verification.

SPECIFICATION:

{description}


CODE:

{code}


TESTS:

{tests}


STATIC ANALYSIS:

{analysis}


FAILURE TYPE:

{failure_type}


FAILURE DETAILS:

{error}


Your task is to correct ONLY the Python implementation.

IMPORTANT:

The SPECIFICATION defines the intended behavior.

You MUST preserve every explicit requirement in the specification.

Use the STATIC ANALYSIS as additional engineering feedback.

If the analysis reports a security warning, avoid introducing
additional unsafe operations when possible.

If the analysis reports complexity concerns, improve the
implementation only when doing so preserves the specified behavior.

Do NOT change specified behavior simply to make one failing
test pass.

If the tests appear inconsistent with the specification,
follow the specification.

IMPORTANT DEBUGGING RULES:

1. Fix the root cause.
2. Preserve the intended functionality.
3. Preserve all explicit edge-case behavior.
4. Preserve specified return values.
5. Do not modify the tests.
6. Do not introduce infinite loops.
7. Do not introduce unnecessary dangerous operations.
8. Return the COMPLETE corrected implementation.

OUTPUT RULES:

1. Return ONLY Python code.
2. DO NOT return tests.
3. DO NOT include assert statements.
4. DO NOT include test functions.
5. DO NOT include filenames.
6. DO NOT include explanations.
7. DO NOT use markdown.
8. Do not surround the code with ```.

Return ONLY the corrected Python implementation.
"""