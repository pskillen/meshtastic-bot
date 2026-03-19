---
name: meshflow-git-workflow
description: >-
  Git workflow for Meshflow (meshflow-api, meshtastic-bot, meshtastic-bot-ui).
  Plan with GitHub issues, branch by issue number, use conventional commits,
  open PRs with linked tickets. Use when starting features, committing, or
  opening pull requests in any Meshflow repo.
---

# Meshflow Git Workflow

## Overview

When working on a feature across meshflow-api, meshtastic-bot, or meshtastic-bot-ui, follow this workflow: plan → issue → branch → commit → PR.

---

## 1. Planning and Issues

**Single-repo work**: Create one issue in the relevant repo with the plan.

**Multi-repo work**: Create a parent issue in meshflow-api and child issues in each affected repo. Link children to the parent.

---

## 2. Branch Naming

Format: `{repo-prefix}-{issue-number}/{author}/{short-description}`

| Repo | Prefix | Example |
|------|--------|---------|
| meshflow-api | `api` | `api-456/paddy/fix-endpoint-bug` |
| meshtastic-bot | `bot` | `bot-123/paddy/add-traceroute-command` |
| meshtastic-bot-ui | `ui` | `ui-78/paddy/add-cool-new-page` |

Use kebab-case for the description. Keep it short.

---

## 3. Pre-commit Formatting

**Before committing**, run the project's formatters:

### meshflow-api

```bash
cd meshflow-api
source venv/bin/activate
cd Meshflow
black .
isort .
flake8 .
```

### meshtastic-bot

```bash
cd meshtastic-bot
source venv/bin/activate
black src/
isort src/
flake8 src/
```

### meshtastic-bot-ui

```bash
cd meshtastic-bot-ui
npm run format
```

---

## 4. Commits

Use [conventional commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Rules**:
- Be brief but descriptive
- Do **not** use the word "enhance"

**Examples**:
```
feat(nodes): add last_heard filter to observed-nodes list
fix(api): correct timezone handling in packet ingestion
refactor(storage): extract packet parsing into service
```

---

## 5. Pull Requests

When the work is done:

1. Open a PR in each affected repository
2. Link the relevant issue(s) in the PR (e.g. "Closes #123")
3. For multi-repo changes, link related PRs between repos in the description

**PR description**: Use the project's `.github/pull_request_template.md` (Summary, Testing performed).

---

## Quick Reference

| Step | Action |
|------|--------|
| Plan | Issue in relevant repo(s); parent in meshflow-api if multi-repo |
| Branch | `{prefix}-{num}/{author}/{description}` |
| Pre-commit | meshflow-api/meshtastic-bot: venv + black, isort, flake8; meshtastic-bot-ui: `npm run format` |
| Commit | Conventional commits, no "enhance" |
| PR | Open in all affected repos, link issues and related PRs |
