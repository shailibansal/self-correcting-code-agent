import re


def extract_python_code(response: str):
    """
    Clean LLM-generated Python code.
    """

    response = response.strip()

    response = re.sub(
        r"```python",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"```",
        "",
        response
    )

    return response.strip()


def extract_python_tests(response: str):
    """
    Extract executable assertion-based tests.

    Removes:
    - markdown fences
    - filenames
    - non-assert statements
    - duplicate assertions
    """

    response = response.strip()

    response = re.sub(
        r"```python",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"```",
        "",
        response
    )

    lines = response.splitlines()

    valid_lines = []
    seen = set()

    for line in lines:

        stripped = line.strip()

        if not stripped:
            continue

        if re.match(
            r"^[\w\-]+\.py$",
            stripped,
            re.IGNORECASE
        ):
            continue

        if stripped.startswith("assert "):

            if stripped not in seen:

                valid_lines.append(line)
                seen.add(stripped)

    return "\n".join(valid_lines).strip()