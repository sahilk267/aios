# AIOS - Documentation Standards

## 1. Overview

This document defines the documentation standards for the AIOS project. Documentation is treated as a first-class deliverable and is maintained alongside code.

## 2. Documentation Philosophy

1. **Docs as Code**: Documentation lives in the repository, reviewed like code
2. **Audience-Specific**: Different docs for different audiences
3. **Living Documents**: Updated with every feature change
4. **Searchable**: Structured for easy navigation and search
5. **Examples Included**: Every feature documented with working examples

## 3. Documentation Types

### 3.1 Architecture Decision Records (ADRs)

**Location**: `docs/adr/`

**When**: Any significant architectural or design decision

**Format**:
```markdown
# ADR-XXX: Title

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
What is the issue motivating this decision?

## Decision
What is the change we're making?

## Consequences
What becomes easier or difficult because of this decision?

## Alternatives Considered
What other options were evaluated?
```

**Numbering**: Sequential (ADR-001, ADR-002, etc.)

### 3.2 API Documentation

**Location**: Auto-generated from code (FastAPI OpenAPI)

**Standards**:
- All endpoints must have summary and description
- All parameters must have description and examples
- All response schemas must be documented
- Error responses must be documented
- Authentication requirements must be specified

**Example**:
```python
@router.post(
    "/agents",
    response_model=AgentResponse,
    summary="Create agent",
    description="Creates a new agent with the specified role and configuration.",
    responses={
        201: {"description": "Agent created successfully"},
        409: {"description": "Agent with this name already exists"},
        422: {"description": "Validation error in request body"},
    },
)
async def create_agent(
    body: AgentCreateRequest,
) -> AgentResponse:
    ...
```

### 3.3 Code Documentation

#### Python Docstrings

Use Google style for all public modules, classes, and functions:

```python
def process_workflow(workflow: Workflow) -> WorkflowResult:
    """Processes a workflow by executing tasks in dependency order.

    This function parses the workflow definition, resolves dependencies,
    and executes tasks in the correct order. Independent tasks are
    executed in parallel.

    Args:
        workflow: The workflow definition containing tasks and dependencies.

    Returns:
        The workflow result containing outputs from all tasks and
        execution metadata.

    Raises:
        WorkflowValidationError: If the workflow definition is invalid.
        CyclicDependencyError: If tasks have circular dependencies.
        TaskExecutionError: If any task fails and retry is exhausted.

    Example:
        workflow = Workflow(tasks=[...])
        result = await process_workflow(workflow)
        print(result.outputs)
    """
```

#### TypeScript/JSDoc

Use JSDoc for all exported functions and components:

```typescript
/**
 * Executes a workflow by running tasks in dependency order.
 *
 * @param workflow - The workflow definition to execute
 * @param options - Execution options including timeout and retry policy
 * @returns Promise resolving to the workflow execution result
 * @throws {WorkflowValidationError} When workflow definition is invalid
 * @throws {TaskExecutionError} When a task fails after all retries
 *
 * @example
 * const result = await executeWorkflow(workflow, {
 *   timeout: 300000,
 *   maxRetries: 3
 * });
 */
export async function executeWorkflow(
  workflow: Workflow,
  options?: ExecutionOptions
): Promise<WorkflowResult> {
```

### 3.4 User Documentation

**Location**: `docs/source/`

**Structure**:
- **Getting Started**: Installation, quickstart, first project
- **User Guide**: Feature-by-feature usage documentation
- **Tutorials**: Step-by-step guides for common tasks
- **FAQ**: Frequently asked questions
- **Troubleshooting**: Common issues and solutions

**Standards**:
- Use clear, concise language
- Include screenshots for UI features
- Provide copy-pasteable command examples
- Link to related documentation
- Note version-specific features
- Include "What's Next" sections

### 3.5 Developer Documentation

**Location**: `docs/source/developer_guide/`

**Contents**:
- Architecture overview
- Development environment setup
- Coding standards reference
- Plugin development guide
- Provider development guide
- Testing guide
- Release process

### 3.6 README Files

Every directory should contain a README.md:

```markdown
# Component Name

Brief description of the component's purpose.

## Responsibilities
- Key responsibility 1
- Key responsibility 2

## Key Interfaces
- Interface1: Description
- Interface2: Description

## Dependencies
- Depends on: Component A, Component B
- Used by: Component C, Component D

## Configuration
| Setting | Default | Description |
|---------|---------|-------------|
| SETTING_NAME | default_value | What it does |

## Usage
\```python
# Example usage
\```

## Testing
\```bash
# How to test this component
pytest tests/unit/test_component.py
\```
```

## 4. Changelog Standards

**Location**: `CHANGELOG.md`

**Format**: Keep a Changelog (https://keepachangelog.com/)

```markdown
# Changelog

## [Unreleased]

### Added
- New feature description

### Changed
- Changed behavior description

### Deprecated
- Soon-to-be removed feature

### Removed
- Removed feature

### Fixed
- Bug fix description

### Security
- Security fix description

## [0.2.0] - 2024-01-15

### Added
- ...

### Changed
- ...

### Fixed
- ...
```

**Rules**:
- Every release gets a changelog entry
- Every PR that changes user-facing behavior gets an entry
- Entries reference issue/PR numbers
- Breaking changes are clearly marked

## 5. Inline Comments

### 5.1 When to Comment

**Good Comments**:
- Why something is done (not what)
- Workarounds for known bugs
- Performance optimizations explained
- Complex algorithm explanations
- Business logic rationale

**Bad Comments**:
- Restating what the code obviously does
- Commented-out code (delete instead)
- Outdated comments
- Joke comments

### 5.2 Comment Format

```python
# Good: Explains why
# We use exponential backoff because the provider rate-limits
# aggressively and immediate retries cause 429 errors.
delay = base_delay * (2 ** attempt)

# Bad: Restates the code
# Set delay to base_delay times 2 to the power of attempt
delay = base_delay * (2 ** attempt)

# TODO format for actionable items
# TODO(username): Refactor this to use the new provider interface
# FIXME(username): This breaks when task has >100 dependencies
# HACK(username): Workaround for Ollama streaming bug
# NOTE(username): This assumes tasks are independent
```

## 6. Wiki and External Documentation

### 6.1 GitHub Wiki
- Quick reference tables
- Comparison matrices
- External resource links

### 6.2 Website Documentation
- Hosted via GitHub Pages
- Built with MkDocs Material
- Auto-generated API reference
- Interactive tutorials

## 7. Documentation Review Process

1. **PR Review**: Documentation changes reviewed like code
2. **Technical Review**: Complex docs reviewed by domain experts
3. **User Testing**: New docs tested by new users for clarity
4. **Freshness Check**: Docs reviewed per release for accuracy

## 8. Documentation Checklist

For each feature:
- [ ] README updated (if new component)
- [ ] API docs updated (OpenAPI)
- [ ] User guide updated
- [ ] Tutorial added (if applicable)
- [ ] Changelog entry added
- [ ] ADR created (if architectural decision)
- [ ] Code comments updated
- [ ] Examples tested and working
