"""AIOS Code Patcher - Safe code modification using AST and unified diff."""

import ast
import difflib
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class PatchResult:
    """Result of a code patch operation."""

    def __init__(
        self,
        success: bool,
        file_path: str,
        original: str,
        patched: str,
        diff: str = "",
        error: str = "",
    ):
        self.success = success
        self.file_path = file_path
        self.original = original
        self.patched = patched
        self.diff = diff
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "file_path": self.file_path,
            "diff": self.diff,
            "error": self.error,
        }


class CodePatcher:
    """Safely modifies code files using AST analysis and unified diffs."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._logger = structlog.get_logger("aios.code_patcher")

    def validate_syntax(self, code: str) -> tuple[bool, str]:
        """Validate Python code syntax using AST."""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"

    def generate_diff(self, original: str, patched: str, file_path: str = "file.py") -> str:
        """Generate unified diff between original and patched code."""
        original_lines = original.splitlines(keepends=True)
        patched_lines = patched.splitlines(keepends=True)
        diff = difflib.unified_diff(
            original_lines,
            patched_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
        )
        return "".join(diff)

    def apply_patch(self, file_path: Path, new_content: str) -> PatchResult:
        """Apply a patch to a file."""
        try:
            original = file_path.read_text() if file_path.exists() else ""

            is_valid, error = self.validate_syntax(new_content)
            if not is_valid:
                return PatchResult(
                    success=False,
                    file_path=str(file_path),
                    original=original,
                    patched=new_content,
                    error=error,
                )

            diff = self.generate_diff(original, new_content, str(file_path))
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(new_content)

            self._logger.info("Patch applied", file=str(file_path))

            return PatchResult(
                success=True,
                file_path=str(file_path),
                original=original,
                patched=new_content,
                diff=diff,
            )

        except Exception as e:
            self._logger.exception("Patch failed", file=str(file_path), error=str(e))
            return PatchResult(
                success=False,
                file_path=str(file_path),
                original="",
                patched=new_content,
                error=str(e),
            )

    def insert_function(
        self,
        file_path: Path,
        function_code: str,
        after_function: str | None = None,
    ) -> PatchResult:
        """Insert a new function into a file."""
        try:
            if file_path.exists():
                content = file_path.read_text()
            else:
                content = '"""Auto-generated module."""\n\n'

            is_valid, error = self.validate_syntax(function_code)
            if not is_valid:
                return PatchResult(
                    success=False,
                    file_path=str(file_path),
                    original=content,
                    patched=content,
                    error=error,
                )

            if after_function:
                tree = ast.parse(content)
                lines = content.split("\n")
                insert_idx = len(lines)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == after_function:
                        insert_idx = node.end_lineno if node.end_lineno else len(lines)
                        break

                lines.insert(insert_idx, "")
                lines.insert(insert_idx + 1, function_code)
                new_content = "\n".join(lines)
            else:
                new_content = content.rstrip() + "\n\n" + function_code + "\n"

            return self.apply_patch(file_path, new_content)

        except Exception as e:
            return PatchResult(
                success=False,
                file_path=str(file_path),
                original="",
                patched="",
                error=str(e),
            )

    def replace_function(
        self,
        file_path: Path,
        function_name: str,
        new_function_code: str,
    ) -> PatchResult:
        """Replace an existing function in a file."""
        try:
            if not file_path.exists():
                return PatchResult(
                    success=False,
                    file_path=str(file_path),
                    original="",
                    patched="",
                    error="File not found",
                )

            content = file_path.read_text()

            is_valid, error = self.validate_syntax(new_function_code)
            if not is_valid:
                return PatchResult(
                    success=False,
                    file_path=str(file_path),
                    original=content,
                    patched=content,
                    error=error,
                )

            tree = ast.parse(content)
            lines = content.split("\n")

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if node.end_lineno else start_line + 1
                    new_lines = lines[:start_line] + new_function_code.split("\n") + lines[end_line:]
                    new_content = "\n".join(new_lines)
                    return self.apply_patch(file_path, new_content)

            return PatchResult(
                success=False,
                file_path=str(file_path),
                original=content,
                patched=content,
                error=f"Function '{function_name}' not found",
            )

        except Exception as e:
            return PatchResult(
                success=False,
                file_path=str(file_path),
                original="",
                patched="",
                error=str(e),
            )

    def add_import(self, file_path: Path, import_statement: str) -> PatchResult:
        """Add an import statement to a file."""
        try:
            content = file_path.read_text() if file_path.exists() else ""

            if import_statement in content:
                return PatchResult(
                    success=True,
                    file_path=str(file_path),
                    original=content,
                    patched=content,
                    error="Import already exists",
                )

            lines = content.split("\n")
            insert_idx = 0

            for i, line in enumerate(lines):
                if line.startswith(("import ", "from ")):
                    insert_idx = i + 1
                elif line.startswith(('"""', "'''")):
                    if i + 1 < len(lines) and lines[i + 1].strip() == "":
                        insert_idx = i + 2
                elif line.strip() and not line.startswith("#"):
                    break

            lines.insert(insert_idx, import_statement)
            new_content = "\n".join(lines)

            return self.apply_patch(file_path, new_content)

        except Exception as e:
            return PatchResult(
                success=False,
                file_path=str(file_path),
                original="",
                patched="",
                error=str(e),
            )
