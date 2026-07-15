def validate_python_syntax(code: str):
    try:
        compile(code, "<string>", "exec")
        return {
            "valid": True,
            "error": ""
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"SyntaxError: {e}"
        }