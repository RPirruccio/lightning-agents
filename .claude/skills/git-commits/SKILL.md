---
name: git-commits
description: Use when writing git commit messages. Follows Conventional Commits specification with proper formatting and scope.
---

# Git Commit Messages

## Quick Start

Follow the Conventional Commits specification for all commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Key Rules**:
- Use imperative mood ("add" not "added")
- Don't capitalize first letter of description
- No period at end of description
- Keep description under 72 characters

---

## Conventional Commits

### Commit Types

| Type | Purpose | SemVer Impact |
|------|---------|---------------|
| **feat** | New feature | MINOR |
| **fix** | Bug fix | PATCH |
| **docs** | Documentation changes | - |
| **style** | Formatting, whitespace (no code change) | - |
| **refactor** | Code change (no bug fix or feature) | - |
| **perf** | Performance improvement | PATCH |
| **test** | Add or correct tests | - |
| **build** | Build system or dependency changes | - |
| **ci** | CI configuration changes | - |
| **chore** | Other changes (no src/test changes) | - |
| **revert** | Revert previous commit | - |

### Format Components

**Type**: Choose from the table above

**Scope** (optional): Component or area affected
- Examples: `auth`, `api`, `db`, `ui`
- Use lowercase, no spaces

**Description**: Brief summary in imperative mood
- Start with lowercase
- No period at end
- Under 72 characters

**Body** (optional): Explain WHAT and WHY, not HOW
- Separate from description with blank line
- Wrap at 72 characters

**Footer** (optional): Reference issues, breaking changes
- Format: `Closes #123` or `Fixes #456`
- Breaking changes: `BREAKING CHANGE: description`

---

## Breaking Changes

Use `!` after type/scope OR add `BREAKING CHANGE:` footer:

```
refactor!: drop support for Node 14

BREAKING CHANGE: Node 14 is no longer supported due to EOL.
Minimum required version is now Node 18.
```

---

## Examples

### Simple Feature
```
feat(auth): add OAuth2 login support
```

### Bug Fix with Body
```
fix(api): prevent null pointer exception in user lookup

The getUserById method was not handling cases where the user
doesn't exist in the database, causing crashes on invalid IDs.

Closes #142
```

### Breaking Change
```
refactor!: drop support for Node 14

BREAKING CHANGE: Node 14 is no longer supported due to EOL.
Minimum required version is now Node 18.
```

### Multiple Changes
```
feat(ui): add dark mode toggle

- Added theme context provider
- Updated button components to use theme
- Persisted preference to localStorage

Closes #89
```

### Documentation
```
docs: update installation instructions for Windows
```

### Refactoring
```
refactor(db): extract connection logic into utility module
```

### Performance
```
perf(api): optimize database query for user search

Reduced query time from 2s to 200ms by adding index
on user.email column.
```

---

## Decision Guide

When writing a commit, ask:

1. **Is this a breaking change?**
   - Yes → Use `!` or `BREAKING CHANGE:` footer
   - No → Continue

2. **What did I do?**
   - Added new capability → `feat`
   - Fixed something broken → `fix`
   - Changed structure, no behavior change → `refactor`
   - Made it faster → `perf`
   - Changed docs only → `docs`
   - Added/fixed tests → `test`

3. **What component was affected?**
   - Clear area → Add scope: `feat(auth):`
   - Multiple areas → Skip scope: `feat:`

4. **Can I explain it in one line?**
   - Yes → Just use description
   - No → Add body explaining WHAT and WHY

---

## Common Patterns

### Multiple Files, One Purpose
```
feat(api): add user profile endpoints

Added GET, PUT, DELETE endpoints for /api/users/:id/profile
```

### Small Refactor
```
refactor: rename getUserId to getCurrentUserId
```

### Dependency Update
```
build: upgrade axios to 1.6.0
```

### CI Fix
```
ci: update GitHub Actions to use Node 18
```

### Reverting a Commit
```
revert: feat(auth): add OAuth2 login support

This reverts commit abc123def456.
Reason: OAuth integration causing timeout issues.
```

---

## Tips

1. **Think audience**: What does a future developer need to know?
2. **Be specific**: "fix(api): handle empty user list" > "fix api bug"
3. **Use conventional types**: Don't invent new ones
4. **Keep it atomic**: One logical change per commit
5. **Reference issues**: Link to tracking systems when applicable

---

## Quick Reference

```
feat: new feature
fix: bug fix
docs: documentation
style: formatting
refactor: restructuring
perf: performance
test: testing
build: build system
ci: continuous integration
chore: maintenance
revert: undo previous commit

! or BREAKING CHANGE: incompatible change
```
