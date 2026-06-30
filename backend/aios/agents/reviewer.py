"""AIOS Reviewer Agent - Code review and quality assurance."""

from typing import Any

import structlog

from aios.agents.base import AgentContext, AgentResult, BaseAgent
from aios.agents.registry import AgentRegistry

logger = structlog.get_logger(__name__)


@AgentRegistry.register
class ReviewerAgent(BaseAgent):
    """Agent responsible for code review and quality assessment.

    The Reviewer agent analyzes code for quality, security, performance,
    and adherence to coding standards.
    """

    ROLE = "reviewer"
    DESCRIPTION = "Reviews code for quality, security, and standards compliance"
    CAPABILITIES = [
        "code_review",
        "quality_assessment",
        "security_review",
        "performance_review",
        "standards_compliance",
    ]

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute code review task."""
        self._logger.info("Reviewer starting", task_id=context.task_id)

        try:
            code = context.input_data.get("code", "")
            files = context.input_data.get("files", [])

            if not code and not files:
                return AgentResult.failure("No code provided for review")

            # Perform review
            review = self._review_code(code, files, context)

            context.add_artifact("review", review)
            context.add_memory("review", f"Completed code review: {review['summary']}")

            return AgentResult.success(
                output=review,
                artifacts={"review": review},
                metrics={
                    "issues_found": len(review["issues"]),
                    "score": review["score"],
                },
            )

        except Exception as e:
            self._logger.exception("Reviewer failed", error=str(e))
            return AgentResult.failure(f"Review failed: {e!s}")

    def _review_code(
        self, code: str, files: list[dict], context: AgentContext
    ) -> dict[str, Any]:
        """Review code and produce findings."""
        issues = []

        # Check for common issues
        if code:
            if "import pdb" in code or "breakpoint()" in code:
                issues.append({
                    "severity": "high",
                    "type": "debug_code",
                    "message": "Debug code found in production code",
                    "suggestion": "Remove debug statements before merging",
                })

            if "except:" in code and "except Exception" not in code:
                issues.append({
                    "severity": "medium",
                    "type": "bare_except",
                    "message": "Bare except clause found",
                    "suggestion": "Use specific exception types",
                })

            if "TODO" in code or "FIXME" in code:
                issues.append({
                    "severity": "low",
                    "type": "todo_found",
                    "message": "TODO/FIXME comments found",
                    "suggestion": "Address TODOs or create tracking issues",
                })

        # Calculate score
        high_count = sum(1 for i in issues if i["severity"] == "high")
        medium_count = sum(1 for i in issues if i["severity"] == "medium")
        low_count = sum(1 for i in issues if i["severity"] == "low")

        score = max(0, 100 - (high_count * 20) - (medium_count * 10) - (low_count * 5))

        return {
            "summary": f"Review complete: {len(issues)} issues found, score: {score}/100",
            "score": score,
            "issues": issues,
            "recommendations": [
                "Add unit tests for new code",
                "Update documentation for API changes",
                "Run security scan before deployment",
            ] if issues else ["Code looks good! No major issues found."],
            "metadata": {
                "created_by": self.name,
                "files_reviewed": len(files) if files else 1,
                "lines_reviewed": len(code.split("\n")) if code else 0,
            },
        }
