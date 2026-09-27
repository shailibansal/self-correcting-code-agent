import subprocess
import tempfile
import os


EXECUTION_TIMEOUT = 5


def execute_python(code: str):
    """
    Execute Python code with a timeout.
    """

    temp_filename = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as temp_file:

            temp_file.write(code)
            temp_filename = temp_file.name

        result = subprocess.run(
            ["py", temp_filename],
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timeout": False
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "stdout": "",
            "stderr": (
                f"Execution timed out after "
                f"{EXECUTION_TIMEOUT} seconds."
            ),
            "timeout": True
        }

    except Exception as e:

        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "timeout": False
        }

    finally:

        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)


def execute_tests(code: str, tests: str):
    """
    Execute Python code together with generated tests
    using a timeout.
    """

    temp_filename = None

    try:

        combined_code = f"""
{code}


# ==========================
# GENERATED TESTS
# ==========================

{tests}
"""

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as temp_file:

            temp_file.write(combined_code)
            temp_filename = temp_file.name

        result = subprocess.run(
            ["py", temp_filename],
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timeout": False
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "stdout": "",
            "stderr": (
                f"Test execution timed out after "
                f"{EXECUTION_TIMEOUT} seconds."
            ),
            "timeout": True
        }

    except Exception as e:

        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "timeout": False
        }

    finally:

        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)