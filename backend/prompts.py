CODE_REVIEW_PROMPT = """
You are an expert Python developer.

Given the following Python code:

1. Find all bugs.
2. Correct the code.
3. Return ONLY the corrected Python code.
4. Do not explain anything.
5. Do not use markdown.
6. Do not surround the code with ```.

Code:
{code}
"""

RETRY_PROMPT = """
The following Python code failed during execution.

Code:
{code}

Error:
{error}

Fix the code.

Return ONLY the corrected Python code.

Do not explain anything.

Do not use markdown.

Do not surround the code with ```.
"""