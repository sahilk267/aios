"""AIOS QA Engineer Agent - Testing and quality assurance."""

import structlog
from typing import Any, Dict, List

from aios.agents.base import BaseAgent, AgentContext, AgentResult
from aios.agents.registry import AgentRegistry

logger = structlog.get_logger(__name__)


@AgentRegistry.register
class QAEngineerAgent(BaseAgent):
    """Agent responsible for testing and quality assurance.
    
    The QA Engineer agent creates test plans, writes test cases,
    and validates implementations against requirements.
    """
    
    ROLE = "qa"
    DESCRIPTION = "Creates tests and validates implementations"
    CAPABILITIES = [
        "test_planning",
        "test_case_generation",
        "unit_testing",
        "integration_testing",
        "test_automation",
    ]
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute QA task."""
        self._logger.info("QA Engineer starting", task_id=context.task_id)
        
        try:
            query = context.input_data.get("query", "")
            implementation = context.input_data.get("implementation", {})
            
            if not query:
                return AgentResult.failure("No query provided for QA")
            
            # Create test plan
            test_plan = self._create_test_plan(query, implementation, context)
            
            context.add_artifact("test_plan", test_plan)
            context.add_memory("qa", f"Created test plan with {len(test_plan['test_cases'])} test cases")
            
            return AgentResult.success(
                output=test_plan,
                artifacts={"test_plan": test_plan},
                metrics={
                    "test_cases": len(test_plan["test_cases"]),
                    "coverage_target": test_plan["coverage_target"],
                },
            )
            
        except Exception as e:
            self._logger.error("QA Engineer failed", error=str(e))
            return AgentResult.failure(f"QA failed: {str(e)}")
    
    def _create_test_plan(
        self, query: str, implementation: Dict, context: AgentContext
    ) -> Dict[str, Any]:
        """Create test plan from query and implementation."""
        return {
            "query": query,
            "test_cases": [
                {
                    "id": "test_happy_path",
                    "name": "Happy Path Test",
                    "type": "unit",
                    "description": "Test normal operation with valid inputs",
                    "priority": "high",
                    "steps": [
                        "Setup test environment",
                        "Execute function with valid inputs",
                        "Assert expected output",
                    ],
                },
                {
                    "id": "test_edge_cases",
                    "name": "Edge Case Tests",
                    "type": "unit",
                    "description": "Test boundary conditions and edge cases",
                    "priority": "high",
                    "steps": [
                        "Test with empty inputs",
                        "Test with maximum values",
                        "Test with special characters",
                    ],
                },
                {
                    "id": "test_error_handling",
                    "name": "Error Handling Tests",
                    "type": "unit",
                    "description": "Test error conditions and exceptions",
                    "priority": "medium",
                    "steps": [
                        "Test with invalid inputs",
                        "Test with missing requiredTest timeout handling",
                    ],
                },
                {
                    "id": "test_integration",
                    "name": "Integration Test",
                    "type": "integration",
                    "description": "Test component integration",
                    "priority": "medium",
                    "steps": [
                        "Setup integration environment",
                        "Test end-to-end flow",
                        "Verify data consistency",
                    ],
                },
            ],
            "coverage_target": 90,
            "test_framework": "pytest",
            "metadata": {
                "created_by": self.name,
                "total_test_cases": 4,
                "estimated_execution_time": "5 minutes",
            },
        }
