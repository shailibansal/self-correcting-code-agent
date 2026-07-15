import subprocess
import tempfile
import os


def execute_python(code: str):
    try:
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as temp_file:
            temp_file.write(code)
            temp_filename = temp_file.name

        # Execute the file
        result = subprocess.run(
            ["python", temp_filename],
            capture_output=True,
            text=True
        )

        # Delete the temporary file
        os.remove(temp_filename)

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e)
        }