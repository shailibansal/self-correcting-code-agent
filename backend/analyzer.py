import ast


DANGEROUS_MODULES = {
    "os",
    "subprocess",
    "socket",
    "requests",
    "urllib",
    "shutil",
    "ctypes",
    "pickle",
}

DANGEROUS_FUNCTIONS = {
    "eval",
    "exec",
    "compile",
    "__import__",
}


class CodeAnalyzer(ast.NodeVisitor):

    def __init__(self):
        self.security_warnings = []
        self.quality_warnings = []

        self.imports = []
        self.defined_names = set()
        self.used_names = set()

        self.loop_count = 0
        self.nested_loop_depth = 0
        self.max_loop_depth = 0

        self.branch_count = 0
        self.function_count = 0
        self.class_count = 0

    # --------------------------------------------------
    # Imports
    # --------------------------------------------------

    def visit_Import(self, node):

        for alias in node.names:

            module_name = alias.name.split(".")[0]

            self.imports.append(module_name)

            if module_name in DANGEROUS_MODULES:

                self.security_warnings.append(
                    f"Potentially dangerous module imported: "
                    f"{module_name}"
                )

        self.generic_visit(node)

    def visit_ImportFrom(self, node):

        if node.module:

            module_name = node.module.split(".")[0]

            self.imports.append(module_name)

            if module_name in DANGEROUS_MODULES:

                self.security_warnings.append(
                    f"Potentially dangerous module imported: "
                    f"{module_name}"
                )

        self.generic_visit(node)

    # --------------------------------------------------
    # Dangerous function calls
    # --------------------------------------------------

    def visit_Call(self, node):

        if isinstance(node.func, ast.Name):

            function_name = node.func.id

            if function_name in DANGEROUS_FUNCTIONS:

                self.security_warnings.append(
                    f"Potentially dangerous function used: "
                    f"{function_name}()"
                )

        elif isinstance(node.func, ast.Attribute):

            attribute_name = node.func.attr

            if attribute_name in {
                "system",
                "popen",
                "run",
                "Popen",
                "call",
                "check_output",
                "remove",
                "unlink",
                "rmtree",
            }:

                self.security_warnings.append(
                    f"Potentially dangerous operation: "
                    f"{attribute_name}()"
                )

        self.generic_visit(node)

    # --------------------------------------------------
    # File operations
    # --------------------------------------------------

    def visit_With(self, node):

        for item in node.items:

            context_expr = item.context_expr

            if isinstance(context_expr, ast.Call):

                if isinstance(
                    context_expr.func,
                    ast.Name
                ):

                    if context_expr.func.id == "open":

                        self.security_warnings.append(
                            "File access detected using open()."
                        )

        self.generic_visit(node)

    # --------------------------------------------------
    # Loops
    # --------------------------------------------------

    def visit_For(self, node):

        self.loop_count += 1

        self.nested_loop_depth += 1

        self.max_loop_depth = max(
            self.max_loop_depth,
            self.nested_loop_depth
        )

        self.generic_visit(node)

        self.nested_loop_depth -= 1

    def visit_While(self, node):

        self.loop_count += 1

        self.nested_loop_depth += 1

        self.max_loop_depth = max(
            self.max_loop_depth,
            self.nested_loop_depth
        )

        self.generic_visit(node)

        self.nested_loop_depth -= 1

    # --------------------------------------------------
    # Branches
    # --------------------------------------------------

    def visit_If(self, node):

        self.branch_count += 1

        self.generic_visit(node)

    def visit_IfExp(self, node):

        self.branch_count += 1

        self.generic_visit(node)

    # --------------------------------------------------
    # Functions/classes
    # --------------------------------------------------

    def visit_FunctionDef(self, node):

        self.function_count += 1

        self.defined_names.add(node.name)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):

        self.function_count += 1

        self.defined_names.add(node.name)

        self.generic_visit(node)

    def visit_ClassDef(self, node):

        self.class_count += 1

        self.defined_names.add(node.name)

        self.generic_visit(node)

    # --------------------------------------------------
    # Name tracking
    # --------------------------------------------------

    def visit_Name(self, node):

        if isinstance(node.ctx, ast.Store):

            self.defined_names.add(node.id)

        elif isinstance(node.ctx, ast.Load):

            self.used_names.add(node.id)

        self.generic_visit(node)


def analyze_code(code: str):
    """
    Perform AST-based static analysis.
    """

    try:

        tree = ast.parse(code)

    except SyntaxError as e:

        return {
            "valid": False,
            "risk_level": "UNKNOWN",
            "security_warnings": [],
            "quality_warnings": [],
            "complexity": {},
            "error": f"SyntaxError: {e}"
        }

    analyzer = CodeAnalyzer()

    analyzer.visit(tree)

    # --------------------------------------------------
    # Quality warnings
    # --------------------------------------------------

    quality_warnings = list(
        analyzer.quality_warnings
    )

    if analyzer.max_loop_depth >= 2:

        quality_warnings.append(
            "Nested loops detected. "
            "Review time complexity."
        )

    if analyzer.loop_count >= 3:

        quality_warnings.append(
            "Multiple loops detected. "
            "Consider reviewing algorithmic complexity."
        )

    if analyzer.branch_count >= 5:

        quality_warnings.append(
            "High number of conditional branches detected."
        )

    # --------------------------------------------------
    # Risk level
    # --------------------------------------------------

    if analyzer.security_warnings:

        risk_level = "HIGH"

    elif quality_warnings:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"

    return {
        "valid": True,

        "risk_level": risk_level,

        "security_warnings":
            analyzer.security_warnings,

        "quality_warnings":
            quality_warnings,

        "complexity": {
            "functions":
                analyzer.function_count,

            "classes":
                analyzer.class_count,

            "loops":
                analyzer.loop_count,

            "max_loop_depth":
                analyzer.max_loop_depth,

            "branches":
                analyzer.branch_count
        },

        "imports":
            analyzer.imports
    }