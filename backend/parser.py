import re


def extract_python_code(response: str):

    # Remove markdown code blocks
    response = re.sub(r"```python", "", response)
    response = re.sub(r"```", "", response)

    return response.strip()