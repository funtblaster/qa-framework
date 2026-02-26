# CI/CD Integration Guide — QA Automation Framework

## Overview

This guide covers the complete CI/CD strategy for your Python + Playwright + pytest framework.
Three GitHub Actions workflows are provided, each serving a distinct role in the pipeline.

---

## Pipeline Architecture

```
Developer pushes / opens PR
        │
        ▼
┌───────────────────┐     parallel
│  1. Lint & Types  │────────────────┐
└───────────────────┘                │
                                     ▼
                          ┌──────────────────────┐
                          │ 2. PR Gate           │
                          │  smoke & p0 tests    │
                          │  split: api | ui     │
                          └──────────┬───────────┘
                                     │ passes
                                     ▼
                               PR can merge
                                     │
                          ┌──────────┴───────────┐
                          │                      │
                          ▼                      ▼
                   Every night            On release tag
              ┌─────────────────┐    ┌─────────────────────┐
              │ 3. Nightly       │    │ 4. Release Gate      │
              │  Full regression │    │  P0 smoke on prod    │
              │  chromium +      │    │  (blocks deploy)     │
              │  firefox +       │    └─────────────────────┘
              │  webkit          │
              └─────────────────┘
```

---

## Workflow Files

### `pr_gate.yml` — Runs on every PR and push to `main`/`develop`

**What it does:**
- Runs `ruff`, `black --check`, and `mypy` as a fast parallel lint job
- Runs `smoke or p0` tests split into two matrix legs: `api` and `ui`
- Publishes JUnit XML results as GitHub PR check annotations
- Uploads screenshots and Playwright traces on failure
- Enforces an 80% code coverage minimum as a separate gate job

**Key design decisions:**
- `needs: lint` — tests only run after linting passes, saving runner minutes
- `fail-fast: false` — API and UI legs both report even if one fails (better signal)
- `concurrency` + `cancel-in-progress` — stale runs from force pushes are cancelled automatically

**Secrets required:**
```
STAGING_BASE_URL
STAGING_API_BASE_URL
STAGING_TEST_USERNAME
STAGING_TEST_PASSWORD
STAGING_API_TOKEN
```

---

### `nightly.yml` — Runs at 02:00 UTC every night

**What it does:**
- Runs the full test suite across all three browsers (chromium, firefox, webkit) in parallel matrix jobs
- Aggregates Allure results from all browser legs and publishes a single report to GitHub Pages
- Sends a rich Slack notification (pass or fail) with links to the run and the report
- Supports `workflow_dispatch` with inputs for environment, browser filter, and custom markers

**Manual trigger with inputs:**
```
environment: staging | production
browser:     all | chromium | firefox | webkit
test_markers: "p1 and api"    ← any valid pytest -m expression
```

**Secrets required (in addition to PR gate secrets):**
```
SLACK_WEBHOOK_URL
GITHUB_TOKEN   ← auto-provided, needed for GitHub Pages deploy
```

---

### `release_gate.yml` — Runs on `v*.*.*` tags or manually

**What it does:**
- Uses GitHub Environments with optional approval gates (configure in repo Settings → Environments)
- Runs only `p0 or smoke` tests against the target environment
- Fails the workflow (and blocks the deployment) if any test fails
- Retains artifacts for 90 days (longer than regular runs)

**To require a manual approval before tests run against production:**
1. Go to **Settings → Environments → production**
2. Enable **Required reviewers**
3. Tag a release: `git tag v1.2.3 && git push --tags`

---

## Required GitHub Repository Setup

### 1. Secrets

Add these in **Settings → Secrets and variables → Actions**:

| Secret | Description |
|---|---|
| `STAGING_BASE_URL` | UI base URL for staging |
| `STAGING_API_BASE_URL` | API base URL for staging |
| `STAGING_TEST_USERNAME` | Test user login |
| `STAGING_TEST_PASSWORD` | Test user password |
| `STAGING_API_TOKEN` | Bearer token for API tests |
| `SLACK_WEBHOOK_URL` | Incoming webhook for nightly notifications |

For the release gate, mirror the above without the `STAGING_` prefix, scoped to each **GitHub Environment**.

### 2. Branch Protection Rules

In **Settings → Branches → Add rule** for `main`:

- ✅ Require status checks to pass before merging
  - Add: `Lint & Type Check`
  - Add: `Smoke & P0 Tests (api)`
  - Add: `Smoke & P0 Tests (ui)`
  - Add: `Coverage Gate`
- ✅ Require branches to be up to date before merging
- ✅ Require linear history (optional but recommended)

### 3. GitHub Pages (for Allure reports)

In **Settings → Pages**:
- Source: `Deploy from a branch`
- Branch: `gh-pages` / `/ (root)`

The nightly workflow will publish the report automatically after each run.

---

## Local Development

The `Makefile` mirrors all CI commands so developers can reproduce failures locally:

```bash
# Run the same check that CI runs on a PR
make test-pr

# Run a specific test type
make test-api
make test-ui

# Run linting
make lint

# Full nightly suite
make test-nightly

# Open Allure report in browser after a run
make test-report
```

---

## Pytest Markers Strategy

Your `pytest.ini` defines a clear marker hierarchy. Use them consistently:

| Marker | When to apply | Run in |
|---|---|---|
| `smoke` | Basic sanity — app is up, login works | PR gate + nightly |
| `p0` | Critical user journeys — must never fail | PR gate + nightly + release |
| `p1` | High priority features | Nightly |
| `p2` | Medium priority | Nightly |
| `flaky` | Known-unreliable — quarantined | Never in CI (exclude explicitly) |
| `slow` | >10 seconds | Nightly only |

**Exclude flaky tests in CI:**
```bash
pytest -m "not flaky" ...
```

**Recommended addition to `pytest.ini`:**
```ini
addopts =
    ...
    -m "not flaky"    ← add this so flaky tests are skipped by default everywhere
```

---

## Handling Flaky Tests

The framework already includes `pytest-rerunfailures` (2 reruns, 1s delay). For CI:

1. Mark known-flaky tests with `@pytest.mark.flaky`
2. Track them in a separate flaky test report (consider a dedicated nightly job)
3. Fix or delete flaky tests within a sprint — don't let the quarantine list grow

---

## Scaling Up

When your suite grows beyond ~15 minutes in the nightly run, consider:

**Test sharding across multiple runners:**
```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]

- name: Run shard ${{ matrix.shard }} of 4
  run: pytest --shard=${{ matrix.shard }}/4 ...   # requires pytest-shard plugin
```

**Separate slow tests into their own job:**
```yaml
- name: Run fast tests
  run: pytest -m "not slow"

- name: Run slow tests
  run: pytest -m "slow"
```

---

## Allure Report URL

After the first nightly run completes, your report will be available at:
```
https://<your-github-org>.github.io/<repo-name>/
```
