#!/usr/bin/env python3
"""AIOS State Validation Script.

Validates the consistency of all state management files.
Run this periodically to ensure project state integrity.
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent


def validate_project_state() -> List[Tuple[str, str]]:
    """Validate PROJECT_STATE.json."""
    errors = []
    state_file = PROJECT_ROOT / "PROJECT_STATE.json"
    
    if not state_file.exists():
        errors.append(("PROJECT_STATE.json", "File not found"))
        return errors
    
    try:
        with open(state_file) as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(("PROJECT_STATE.json", f"Invalid JSON: {e}"))
        return errors
    
    # Check required fields
    required_fields = ["project", "version", "status", "phase", "modules"]
    for field in required_fields:
        if field not in state:
            errors.append(("PROJECT_STATE.json", f"Missing field: {field}"))
    
    # Validate module statuses
    if "modules" in state:
        valid_statuses = {"pending", "in_progress", "completed", "failed"}
        for module_name, module_data in state["modules"].items():
            if "status" in module_data and module_data["status"] not in valid_statuses:
                errors.append((
                    "PROJECT_STATE.json",
                    f"Module '{module_name}' has invalid status: {module_data['status']}"
                ))
    
    return errors


def validate_tasks() -> List[Tuple[str, str]]:
    """Validate TASKS.md."""
    errors = []
    tasks_file = PROJECT_ROOT / "TASKS.md"
    
    if not tasks_file.exists():
        errors.append(("TASKS.md", "File not found"))
        return errors
    
    content = tasks_file.read_text()
    
    # Check for required sections
    required_sections = ["Active Tasks", "Completed Tasks"]
    for section in required_sections:
        if section not in content:
            errors.append(("TASKS.md", f"Missing section: {section}"))
    
    return errors


def validate_roadmap() -> List[Tuple[str, str]]:
    """Validate ROADMAP.md."""
    errors = []
    roadmap_file = PROJECT_ROOT / "ROADMAP.md"
    
    if not roadmap_file.exists():
        errors.append(("ROADMAP.md", "File not found"))
        return errors
    
    content = roadmap_file.read_text()
    
    # Check for required sections
    required_sections = ["Current Status", "Phase Overview"]
    for section in required_sections:
        if section not in content:
            errors.append(("ROADMAP.md", f"Missing section: {section}"))
    
    return errors


def validate_changelog() -> List[Tuple[str, str]]:
    """Validate CHANGELOG.md."""
    errors = []
    changelog_file = PROJECT_ROOT / "CHANGELOG.md"
    
    if not changelog_file.exists():
        errors.append(("CHANGELOGLOG.md", "File not found"))
        return errors
    
    content = changelog_file.read_text()
    
    if "## [Unreleased]" not in content:
        errors.append(("CHANGELOG.md", "Missing [Unreleased] section"))
    
    return errors


def validate_file_references() -> List[Tuple[str, str]]:
    """ exist."""
    errors = []
    
    # Check that key files exist
    key_files = [
        "SRS.md",
        "SystemDesign.md",
        "RepositoryStructure.md",
        "ImplementationRoadmap.md",
        "Milestones.md",
        "DependencyGraph.md",
        "ArchitectureDiagrams.md",
        "RiskAnalysis.md",
        "CodingStandards.md",
        "DocumentationStandards.md",
        "TestingStandards.md",
        "ContributionGuide.md",
        "AIGovernanceRules.md",
        "DECISIONS.md",
        "KNOWLEDGE_BASE.md",
        "AI_MEMORY.md",
        "SELF_IMPROVEMENT.md",
        "INDEXING_STRATEGY.md",
    ]
    
    for file_name in key_files:
        if not (PROJECT_ROOT / file_name).exists():
            errors.append(("File Reference", f"Missing file: {file_name}"))
    
    return errors


def main():
    """Run all validations."""
    print("=" * 60)
    print("AIOS State Validation")
    print("=" * 60)
    
    all_errors: List[Tuple[str, str]] = []
    
    validators = [
        ("PROJECT_STATE.json", validate_project_state),
        ("TASKS.md", validate_tasks),
        ("ROADMAP.md", validate_roadmap),
        ("CHANGELOG.md", validate_changelog),
        ("File References", validate_file_references),
    ]
    
    for name, validator in validators:
        errors = validator()
        if errors:
            print(f"\n❌ {name}:")
            for file, error in errors:
                print(f"   - {error}")
            all_errors.extend(errors)
        else:
            print(f"\n✅ {name}: Valid")
    
    print("\n" + "=" * 60)
    
    if all_errors:
        print(f"Validation FAILED: {len(all_errors)} error(s) found")
        sys.exit(1)
    else:
        print("Validation PASSED: All state files are consistent")
        sys.exit(0)


if __name__ == "__main__":
    main()
