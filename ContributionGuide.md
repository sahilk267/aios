# AIOS - Contribution Guide

## 1. Welcome

Thank you for your interest in contributing to AIOS! This guide will help you get started with contributing to the project.

## 2. Code of Conduct

All contributors must adhere to our Code of Conduct. Be respectful, inclusive, and constructive in all interactions.

## 3. Getting Started

### 3.1 Prerequisites

- Python 3.11+
- Node.js 20+
- Rust 1.70+ (for Tauri frontend)
- Git 2.40+
- Docker (optional, for containerized tools)

### 3.2 Development Setup

```bash
# Clone the repository
git clone https://github.com/aios-project/aios.git
cd aios

# Run the setup script
./scripts/setup.sh

# Or manual setup:
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Frontend
cd ../frontend
npm install

# Run database migrations
cd ../backend
alembic upgrade head

# Start development servers
./scripts/dev.sh
```

### 3.3 Development Servers

| Server | URL | Description |
|--------|-----|-------------|
| Backend API | http://localhost:8000 | FastAPI backend |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Frontend | http://localhost:5173 | Vite dev server |
| Tauri | Desktop app | Production-like |

## 4. How to Contribute

### 4.1 Reporting Bugs

1. Check existing issues first
2. Use the bug report template
3. Include:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details
   - Screenshots/logs if applicable

### 4.2 Requesting Features

1. Check existing feature requests
2. Use the feature request template
3. Describe the problem it solves
4. Suggest implementation approach if possible

### 4.3 Contributing Code

1. **Fork and Branch**: Fork the repo, create a branch from `develop`
2. **Pick an Issue**: Look for `good first issue` or `help wanted` labels
3. **Discuss**: Comment on the issue to coordinate
4. **Implement**: Follow coding standards
5. **Test**: Write tests for your changes
6. **Document**: Update relevant documentation
7. **PR**: Submit a pull request to `develop`

### 4.4 Pull Request Process

1. **Before Submitting**:
   - Code follows coding standards
   - All tests pass
   - New tests added for new functionality
   - Documentation updated
   - Changelog entry added
   - No merge conflicts

2. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes.

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Related Issue
   Closes #issue_number

   ## Testing
   How was this tested?

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-reviewed code
   - [ ] Added tests
   - [ ] Updated docs
   - [ ] Added changelog entry
   ```

3. **Review Process**:
   - At least one maintainer review required
   - CI must pass
   - Code coverage must not decrease
   - All review comments addressed

## 5. Development Workflow

### 5.1 Branch Strategy

```
main (production releases)
├── develop (integration branch)
│   ├── feature/*
│   ├── bugfix/*
│   └── plugin/*
├── release/*
└── hotfix/*
```

### 5.2 Commit Convention

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no logic change)
- `refactor`: Code restructuring
- `test`: Adding/fixing tests
- `chore`: Maintenance
- `perf`: Performance improvement
- `ci`: CI changes
- `build`: Build system changes

**Examples**:
```
feat(agent): add parallel task execution

fix(memory): resolve session cleanup bug

docs(api): update authentication guide
```

### 5.3 Code Review Guidelines

**As a Reviewer**:
- Be constructive and specific
- Explain the "why" behind suggestions
- Distinguish between must-fix and nice-to-have
- Approve when comments are addressed

**As an Author**:
- Respond to all comments
- Explain decisions when disagreeing
- Make requested changes promptly
- Re-request review when ready

## 6. Project Structure

```
aios/
├── backend/          # Python backend
│   ├── aios/        # Main application code
│   └── tests/       # Test suite
├── frontend/         # Tauri/React frontend
│   ├── src/         # Source code
│   └── src-tauri/   # Tauri Rust code
├── docs/            # Documentation
├── plugins/         # Plugin examples
└── scripts/         # Build/dev scripts
```

## 7. Key Areas for Contribution

### 7.1 Good First Issues
- Documentation improvements
- Test coverage additions
- UI polish and accessibility
- Error message improvements
- Configuration validation

### 7.2 Help Wanted
- New agent implementations
- Provider integrations
- Plugin development
- Performance optimization
- Platform-specific fixes

### 7.3 Advanced Areas
- Workflow engine improvements
- Memory system enhancements
- Security hardening
- Architecture refactoring

## 8. Plugin Development

### 8.1 Creating a Plugin

1. Use the plugin template:
   ```bash
   aios plugin create my-plugin --type=agent
   ```

2. Implement the plugin interface:
   ```python
   from aios.plugins import BasePlugin, PluginMetadata

   class MyAgentPlugin(BasePlugin):
       metadata = PluginMetadata(
           name="my-agent",
           version="0.1.0",
           author="Your Name",
           plugin_type="agent",
       )

       async def execute(self, context: PluginContext) -> PluginResult:
           # Implementation
           pass
   ```

3. Test locally:
   ```bash
   aios plugin test my-plugin
   ```

4. Publish:
   ```bash
   aios plugin publish my-plugin
   ```

### 8.2 Plugin Guidelines

- Follow the plugin API contract
- Handle errors gracefully
- Include comprehensive tests
- Document configuration options
- Respect resource limits
- No network calls without user consent

## 9. Testing Requirements

- Unit tests for all new code
- Integration tests for API changes
- E2E tests for UI changes
- Coverage must not decrease
- Tests must be deterministic

## 10. Documentation Requirements

- Update README for new components
- Add docstrings to public APIs
- Update user guide for new features
- Add changelog entry
- Include code examples

## 11. Community

- **Discord**: [Join our server](https://discord.gg/aios)
- **Discussions**: Use GitHub Discussions for questions
- **Weekly Sync**: Thursdays 15:00 UTC (announced in Discord)
- **Monthly Community Call**: First Friday of each month

## 12. Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Annual contributor spotlight
- Contributor badges on Discord

## 13. License

By contributing to AIOS, you agree that your contributions will be licensed under the project's Apache-2.0 license.
