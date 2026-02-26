# Contributing to qa-framework

Thank you for your interest in contributing! This document outlines the process for reporting bugs, proposing changes, and submitting pull requests.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Submitting a Pull Request](#submitting-a-pull-request)
- [Development Setup](#development-setup)
- [Branch & Commit Conventions](#branch--commit-conventions)
- [Test Guidelines](#test-guidelines)
- [Code Style](#code-style)
- [Review Process](#review-process)

---

## Code of Conduct

Please be respectful and constructive in all interactions. We expect contributors to maintain a welcoming and inclusive environment for everyone.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/qa-framework.git
   cd qa-framework
   ```
3. **Add the upstream remote** to stay in sync:
   ```bash
   git remote add upstream https://github.com/funtblaster/qa-framework.git
   ```

---

## How to Contribute

### Reporting Bugs

Before opening a bug report, please search existing [Issues](https://github.com/funtblaster/qa-framework/issues) to avoid duplicates.

When filing a bug, please include:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behaviour
- Your environment (OS, Python version, browser if relevant)
- Relevant logs or screenshots

### Suggesting Features

Open an Issue with the label `enhancement` and describe:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

### Submitting a Pull Request

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
2. Make your changes, following the guidelines below.
3. Ensure all tests pass locally:
   ```bash
   make test
   ```
4. Push your branch and open a PR against `main`.
5. Fill in the PR template, linking any related Issues.

PRs must pass the **PR Gate** CI check (smoke + p0 tests) before review.

---

## Development Setup

```bash
# Install dependencies (including dev extras)
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium

# Copy and configure your local environment
cp config/environments/local.env .env
# Edit .env with your BASE_URL, credentials, etc.

# Verify everything works
make test
```

---

## Branch & Commit Conventions

| Type | Branch prefix | Example |
|---|---|---|
| New feature | `feat/` | `feat/add-retry-logic` |
| Bug fix | `fix/` | `fix/flaky-login-test` |
| Documentation | `docs/` | `docs/update-readme` |
| Refactor | `refactor/` | `refactor/api-client` |
| CI/tooling | `chore/` | `chore/update-deps` |

Commit messages should follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(utils): add exponential backoff to retry helper
fix(ui): correct locator for submit button on checkout page
docs: add CONTRIBUTING guide
```

---

## Test Guidelines

- **New features** must include corresponding tests.
- **Bug fixes** should include a regression test.
- Tag tests appropriately with pytest markers (`@pytest.mark.smoke`, `@pytest.mark.p0`, etc.).
- UI tests must use Page Object Models located in `tests/ui/pages/`.
- API tests must use the shared `api_client` fixture.
- Avoid hardcoded URLs, credentials, or environment-specific values — use the config layer.

Run targeted test subsets before pushing:

```bash
make test-api       # API tests only
make test-ui        # UI tests only
pytest -m smoke     # Smoke checks only
```

---

## Code Style

This project uses the following tools (configured in `pyproject.toml`):

| Tool | Purpose |
|---|---|
| `black` | Code formatting |
| `isort` | Import ordering |
| `flake8` | Linting |
| `mypy` | (Optional) type checking |

Run formatting before committing:

```bash
black .
isort .
flake8 .
```

Or via Make (if configured):

```bash
make lint
make format
```

---

## Review Process

- A maintainer will review your PR within a few business days.
- Feedback will be given as inline comments — please respond or resolve each one.
- Once approved and CI passes, a maintainer will merge using **squash merge** to keep history clean.
- Large changes may require discussion in an Issue before a PR is accepted.

---

Thank you for helping make this framework better! 🙌
