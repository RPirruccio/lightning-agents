---
name: dead-code-detection
description: Use when finding and cleaning dead code in Python. Covers vulture usage, false positive patterns, whitelist strategies, and safe cleanup procedures.
---

# Dead Code Detection with Vulture

You are a dead code detection specialist. This skill provides comprehensive guidance on using vulture to find unused code and safely clean it up while avoiding false positives.

## Quick Start

When cleaning dead code:

1. **Scan first**: Run vulture to identify candidates
2. **Analyze confidence**: Check the confidence percentage (60-100%)
3. **Identify false positives**: Apply patterns below to filter
4. **Create whitelist**: Document intentional unused code
5. **Clean safely**: Remove only confirmed dead code
6. **Verify**: Run tests after cleanup

## Running Vulture

### Basic Usage

```bash
# Scan a directory
vulture src/

# Scan with minimum confidence threshold
vulture src/ --min-confidence 80

# Scan specific files
vulture src/main.py src/utils.py

# Include a whitelist file
vulture src/ whitelist.py

# Sort by confidence (highest first)
vulture src/ --sort-by-size
```

### Understanding Output

```
src/utils.py:42: unused function 'helper_func' (60% confidence)
src/models.py:15: unused class 'LegacyModel' (100% confidence)
src/api.py:8: unused import 'json' (90% confidence)
```

**Confidence levels:**
- **100%**: Definitely unused in scanned files
- **80-99%**: Very likely unused
- **60-79%**: Possibly unused, needs verification

## Common False Positive Patterns

### 1. Framework Magic Methods

These are called by frameworks, not directly in code:

```python
# Django
class MyModel(models.Model):
    class Meta:           # ← Framework uses this
        ordering = ['name']

    def save(self, *args, **kwargs):  # ← Override, framework calls it
        super().save(*args, **kwargs)

# Flask/FastAPI
@app.route('/api/users')
def get_users():  # ← Called by framework routing
    return users

# Pytest
def test_something():  # ← Called by test runner
    assert True

def pytest_configure(config):  # ← Pytest hook
    pass
```

**Whitelist pattern:**
```python
# whitelist.py
_.Meta  # Django Meta classes
_.save  # Django model save override
_.clean  # Django model validation
_.get_queryset  # Django manager method
test_*  # Pytest test functions
pytest_*  # Pytest hooks
```

### 2. Dunder Methods

Special Python methods called implicitly:

```python
class MyClass:
    def __init__(self):    # Constructor
        pass
    def __str__(self):     # Called by str()
        return "MyClass"
    def __repr__(self):    # Called by repr()
        return "MyClass()"
    def __len__(self):     # Called by len()
        return 0
    def __iter__(self):    # Called by iteration
        yield
    def __enter__(self):   # Context manager
        return self
    def __exit__(self, *args):  # Context manager
        pass
```

**These are almost always false positives** - vulture may miss their implicit usage.

### 3. Public API / Exported Names

Code designed for external import:

```python
# __init__.py
from .utils import process_data, validate_input  # Exported API
from .models import User, Product

__all__ = ['process_data', 'validate_input', 'User', 'Product']
```

**Whitelist pattern:**
```python
# whitelist.py - items in __all__ or __init__.py exports
process_data
validate_input
User
Product
```

### 4. Abstract Methods / Interface Compliance

```python
from abc import ABC, abstractmethod

class BaseHandler(ABC):
    @abstractmethod
    def handle(self, request):  # Must be implemented by subclasses
        pass

class ConcreteHandler(BaseHandler):
    def handle(self, request):  # Required by ABC, may look unused
        return process(request)
```

### 5. Callback / Event Handlers

```python
# Signal handlers
def on_user_created(sender, instance, **kwargs):  # Django signal
    send_welcome_email(instance)

# Event callbacks
def on_click(event):  # GUI callback
    print("Clicked!")

button.bind("<Button-1>", on_click)  # Vulture may not trace this
```

### 6. Celery / Background Tasks

```python
from celery import shared_task

@shared_task
def send_email_async(user_id, message):  # Called via .delay()
    user = User.objects.get(id=user_id)
    send_email(user.email, message)

# Called as: send_email_async.delay(user_id, message)
```

### 7. CLI Entry Points

```python
# In pyproject.toml: [project.scripts] myapp = "mypackage.cli:main"
def main():  # Entry point, called externally
    app.run()

if __name__ == "__main__":
    main()
```

### 8. Pydantic/Dataclass Validators

```python
from pydantic import BaseModel, field_validator

class UserModel(BaseModel):
    email: str

    @field_validator('email')
    def validate_email(cls, v):  # Called by Pydantic, not directly
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
```

### 9. Unused Variables with Purpose

```python
# Intentional tuple unpacking
first, *rest, last = items
_ = ignored_value  # Convention for ignored

# Loop variable for count only
for _ in range(10):
    do_something()

# Exception binding
try:
    risky_operation()
except ValueError as e:  # 'e' may be unused but documents exception
    log_error()
```

## Creating Whitelists

### Whitelist File Format

Create `vulture_whitelist.py` (or any `.py` file):

```python
# vulture_whitelist.py
# This file documents intentionally unused code

# Django patterns
_.Meta
_.save
_.clean
_.delete
_.get_absolute_url
_.get_queryset

# Framework magic
test_*  # Pytest tests
pytest_*  # Pytest hooks
setup_*  # Pytest fixtures
teardown_*

# Public API exports
from mypackage import (
    public_function,
    PublicClass,
    EXPORTED_CONSTANT,
)

# Callbacks and handlers
on_*  # Event handlers
handle_*  # Request handlers

# CLI entry points
main
cli
run

# Celery tasks (mark with decorator in actual code)
_.delay
_.apply_async
```

### Generating Whitelists

```bash
# Generate whitelist from vulture output
vulture src/ --make-whitelist > vulture_whitelist.py

# Then edit to remove actual dead code
```

## Safe Cleanup Workflow

### Step 1: Initial Scan

```bash
# Get high-confidence dead code first
vulture src/ --min-confidence 90
```

### Step 2: Categorize Results

For each item, determine:

| Category | Action |
|----------|--------|
| Confirmed dead | Remove it |
| False positive | Add to whitelist |
| Uncertain | Investigate further |

### Step 3: Investigate Uncertain Items

```bash
# Search for dynamic usage
grep -r "getattr.*function_name" src/
grep -r "'function_name'" src/
grep -r '"function_name"' src/

# Check if it's in __all__
grep -r "__all__" src/

# Check imports in __init__.py
cat src/package/__init__.py
```

### Step 4: Remove Confirmed Dead Code

For each confirmed dead code item:

1. **Read the surrounding context** - understand what it was for
2. **Check git blame** - see when/why it was added
3. **Remove carefully** - may need to remove related code
4. **Run tests** - verify nothing broke

### Step 5: Update Whitelist

After cleanup, regenerate whitelist for remaining false positives:

```bash
vulture src/ whitelist.py --make-whitelist > new_whitelist.py
# Review and merge with existing whitelist
```

## Integration Patterns

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/jendrikseipp/vulture
    rev: v2.10
    hooks:
      - id: vulture
        args: [src/, vulture_whitelist.py, --min-confidence, "80"]
```

### CI/CD Pipeline

```yaml
# GitHub Actions
- name: Check for dead code
  run: |
    vulture src/ vulture_whitelist.py --min-confidence 80
```

### Makefile

```makefile
.PHONY: dead-code
dead-code:
	vulture src/ vulture_whitelist.py --min-confidence 80

.PHONY: dead-code-whitelist
dead-code-whitelist:
	vulture src/ --make-whitelist > vulture_whitelist.py
```

## Common Mistakes to Avoid

### 1. Removing Code Without Testing

**Wrong:**
```bash
# Remove everything vulture reports
vulture src/ | xargs -I {} sed -i '' 's/{}//'  # DON'T DO THIS
```

**Right:**
```bash
# Remove one item, test, commit, repeat
vulture src/ --min-confidence 100
# Manually review and remove
pytest
git commit -m "Remove unused function X"
```

### 2. Ignoring Low-Confidence Results

Low confidence doesn't mean not dead - investigate:

```bash
vulture src/ --min-confidence 60
# These need manual verification
```

### 3. Not Updating Whitelists

Whitelists become stale as code changes. Regenerate periodically:

```bash
# Check if whitelist items are still needed
vulture vulture_whitelist.py
```

### 4. Deleting Unused but Intentional Code

Some code is intentionally unused:
- Feature flags for future features
- Backwards compatibility code
- Debug utilities
- Template/example code

**Document these in whitelist with comments.**

## Output Format

When reporting dead code findings:

1. **Summary**: Total unused items found, by category
2. **High confidence (90-100%)**: List with file:line
3. **Medium confidence (70-89%)**: List with investigation notes
4. **Identified false positives**: Items to whitelist
5. **Cleanup plan**: Prioritized list of removals

**Example output:**

```
## Dead Code Analysis

### Summary
- Total items found: 23
- Confirmed dead code: 8
- False positives: 12
- Needs investigation: 3

### Confirmed Dead Code (safe to remove)
1. `src/utils.py:42` - `old_helper()` (100% confidence)
   - Last modified: 2023-01-15
   - No references found in codebase

2. `src/models.py:89` - `LegacyUser` class (100% confidence)
   - Replaced by `User` class in refactor
   - No imports or usage

### False Positives (add to whitelist)
1. `src/api.py:15` - `handle_request()` (90% confidence)
   - Reason: Flask route handler

2. `src/tasks.py:8` - `send_notification()` (80% confidence)
   - Reason: Celery task called via .delay()

### Needs Investigation
1. `src/helpers.py:33` - `format_date()` (70% confidence)
   - May be dynamically called via getattr
   - Check: grep -r "format_date" src/
```
