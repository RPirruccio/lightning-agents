---
name: python-documentation
description: Use when writing Python docstrings, documenting functions/classes, or creating API documentation. Covers Google and NumPy docstring styles.
---

# Python Documentation

You are a technical documentation specialist for Python code. This skill provides guidance on writing clear, concise documentation for Python functions, classes, and modules.

## Quick Start

When documenting a Python function or class:

1. Choose a docstring style (Google or NumPy) and be consistent
2. Write a one-line summary describing WHAT it does (not HOW)
3. Document all parameters with types and descriptions
4. Document the return value and its type
5. List any exceptions that may be raised
6. Include a brief usage example when helpful

## Docstring Styles

### Google Style (Recommended for Most Projects)

Google style is clean, readable, and widely adopted.

**Function Example:**
```python
def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate the Euclidean distance between two points.

    Args:
        x1: X-coordinate of the first point
        y1: Y-coordinate of the first point
        x2: X-coordinate of the second point
        y2: Y-coordinate of the second point

    Returns:
        The Euclidean distance between the two points as a float

    Raises:
        ValueError: If any coordinate is NaN or infinite

    Example:
        >>> calculate_distance(0, 0, 3, 4)
        5.0
    """
    if any(math.isnan(c) or math.isinf(c) for c in [x1, y1, x2, y2]):
        raise ValueError("Coordinates must be finite numbers")
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
```

**Class Example:**
```python
class DatabaseConnection:
    """Manages connection to a PostgreSQL database.

    This class handles connection pooling, automatic reconnection,
    and transaction management for PostgreSQL databases.

    Attributes:
        host: Database host address
        port: Database port number
        database: Name of the database
        is_connected: True if connection is active

    Example:
        >>> db = DatabaseConnection("localhost", 5432, "mydb")
        >>> db.connect()
        >>> db.execute_query("SELECT * FROM users")
    """

    def __init__(self, host: str, port: int, database: str):
        """Initialize database connection parameters.

        Args:
            host: Database host address
            port: Database port number (default: 5432)
            database: Name of the database to connect to
        """
        self.host = host
        self.port = port
        self.database = database
        self.is_connected = False
```

### NumPy Style (Recommended for Scientific Computing)

NumPy style is preferred in scientific/data science contexts.

**Function Example:**
```python
def polynomial_fit(x: np.ndarray, y: np.ndarray, degree: int = 2) -> np.ndarray:
    """Fit a polynomial to data points using least squares.

    Parameters
    ----------
    x : np.ndarray
        Input x-coordinates, shape (n,)
    y : np.ndarray
        Input y-coordinates, shape (n,)
    degree : int, optional
        Degree of the polynomial, by default 2

    Returns
    -------
    np.ndarray
        Polynomial coefficients from highest to lowest degree, shape (degree + 1,)

    Raises
    ------
    ValueError
        If x and y have different lengths or degree is negative

    See Also
    --------
    np.polyfit : NumPy's polynomial fitting function
    np.polyval : Evaluate a polynomial

    Examples
    --------
    Fit a quadratic to sample data:

    >>> x = np.array([0, 1, 2, 3, 4])
    >>> y = np.array([0, 1, 4, 9, 16])
    >>> coeffs = polynomial_fit(x, y, degree=2)
    >>> coeffs
    array([1., 0., 0.])

    Notes
    -----
    Uses ordinary least squares regression. For weighted fitting,
    consider using scipy.optimize.curve_fit instead.
    """
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    if degree < 0:
        raise ValueError("degree must be non-negative")
    return np.polyfit(x, y, degree)
```

## Docstring Sections

### 1. Summary Line (Required)

- One line describing WHAT the function/class does
- Use imperative mood: "Calculate distance" not "Calculates distance"
- No period at the end if it's a single phrase
- Keep under 80 characters

**Good Examples:**
- "Calculate the Euclidean distance between two points"
- "Parse JSON configuration file and validate schema"
- "Represent a user account with authentication methods"

**Bad Examples:**
- "This function calculates..." (too verbose)
- "Distance calculator" (not descriptive enough)
- "Uses the Pythagorean theorem to find distance" (describes HOW, not WHAT)

### 2. Extended Description (Optional)

Add a paragraph after the summary if you need to explain:
- Additional context or background
- Important constraints or assumptions
- Relationship to other functions/classes

Leave a blank line after the summary line.

### 3. Parameters (Args/Parameters)

**Google style:** Use `Args:` section
**NumPy style:** Use `Parameters` section with `----------` underline

Format:
- **Google:** `name: Description` or `name (type): Description`
- **NumPy:** `name : type` on one line, description indented on next line

**Guidelines:**
- Use type hints in function signature, then reference types in docstring
- Describe what the parameter represents, not just its type
- Mention default values if not obvious
- Note any constraints (e.g., "must be positive")

### 4. Returns (Required if function returns something)

**Google style:** Use `Returns:` section
**NumPy style:** Use `Returns` section with `-------` underline

Format:
- Describe what is returned and its type
- If returning a tuple, describe each element
- If returning None, either omit the section or state "None"

**Examples:**

Google:
```python
Returns:
    dict: Mapping of user IDs to User objects, or empty dict if no users found
```

NumPy:
```python
Returns
-------
success : bool
    True if operation succeeded
error_msg : str or None
    Error message if operation failed, None otherwise
```

### 5. Raises (Include if applicable)

List exceptions that the function explicitly raises (don't document every possible exception).

**Google style:**
```python
Raises:
    ValueError: If input is empty or contains invalid characters
    FileNotFoundError: If the specified file does not exist
```

**NumPy style:**
```python
Raises
------
ValueError
    If input is empty or contains invalid characters
FileNotFoundError
    If the specified file does not exist
```

### 6. Examples (Highly Recommended)

Provide brief usage examples using doctest format:

```python
Example:
    >>> result = my_function(10, 20)
    >>> print(result)
    30
```

For NumPy style:
```python
Examples
--------
Basic usage:

>>> result = my_function(10, 20)
>>> print(result)
30

With optional parameters:

>>> result = my_function(10, 20, verbose=True)
Processing...
30
```

**Guidelines:**
- Keep examples minimal but illustrative
- Show the most common use case
- Use `>>>` for interactive examples (doctest compatible)
- Include output if it helps understanding

### 7. Additional Sections (NumPy style)

NumPy style supports additional sections:

- **See Also:** Related functions/classes
- **Notes:** Additional technical details, algorithms, references
- **References:** Academic papers, external documentation
- **Warnings:** Important caveats or deprecation notices

## Best Practices

### 1. Focus on WHAT, not HOW

**Good:**
```python
def normalize_text(text: str) -> str:
    """Convert text to lowercase and remove extra whitespace."""
```

**Bad:**
```python
def normalize_text(text: str) -> str:
    """Uses the lower() method and regex to clean up the text."""
```

### 2. Be Concise

Remove unnecessary words while maintaining clarity.

**Good:**
```python
Args:
    timeout: Maximum seconds to wait for response
```

**Bad:**
```python
Args:
    timeout: This parameter specifies the maximum number of seconds that
             the function will wait for a response before timing out
```

### 3. Use Precise Technical Language

**Good:**
```python
Returns:
    Generator yielding tuples of (key, value) pairs
```

**Bad:**
```python
Returns:
    Something that gives you the keys and values
```

### 4. Document Edge Cases and Constraints

```python
def divide(a: float, b: float) -> float:
    """Divide a by b.

    Args:
        a: Numerator
        b: Denominator (must be non-zero)

    Returns:
        The quotient a/b

    Raises:
        ZeroDivisionError: If b is zero
    """
```

### 5. Keep Examples Minimal

Show the most common or important use case:

```python
Example:
    >>> user = User("alice", "alice@example.com")
    >>> user.send_email("Hello!")
```

Don't include every possible parameter combination.

### 6. Use Type Hints in Function Signatures

Prefer this:
```python
def process_data(items: list[str], limit: int = 10) -> dict[str, int]:
    """Count frequency of items up to limit."""
```

Over this:
```python
def process_data(items, limit=10):
    """Count frequency of items up to limit.

    Args:
        items (list[str]): Items to process
        limit (int): Maximum items to process

    Returns:
        dict[str, int]: Frequency mapping
    """
```

Type hints reduce redundancy in docstrings.

### 7. Update Documentation When Code Changes

Outdated documentation is worse than no documentation. When modifying a function:
- Update the summary if behavior changed
- Add/remove parameters as needed
- Update examples if the API changed
- Revise edge cases if constraints changed

## Module and Package Documentation

### Module Docstring

Place at the top of the file:

```python
"""User authentication and authorization utilities.

This module provides functions for user login, password hashing,
token generation, and permission checking.

Typical usage example:

    from myapp.auth import authenticate_user, generate_token

    user = authenticate_user(username, password)
    token = generate_token(user)
"""

import hashlib
import secrets
# ... rest of module
```

### Package Docstring

In `__init__.py`:

```python
"""MyPackage - A toolkit for data processing.

This package provides utilities for loading, transforming,
and analyzing structured data.

Modules:
    loaders: Data loading from various sources
    transforms: Data transformation utilities
    analyzers: Statistical analysis tools
"""

from .loaders import load_csv, load_json
from .transforms import normalize, filter_outliers
from .analyzers import compute_stats

__all__ = ['load_csv', 'load_json', 'normalize', 'filter_outliers', 'compute_stats']
__version__ = '1.0.0'
```

## Common Patterns

### Optional Parameters

```python
def fetch_data(url: str, timeout: int = 30, retries: int = 3) -> dict:
    """Fetch JSON data from a URL with retry logic.

    Args:
        url: URL to fetch from
        timeout: Request timeout in seconds (default: 30)
        retries: Number of retry attempts on failure (default: 3)

    Returns:
        Parsed JSON response as a dictionary
    """
```

### Multiple Return Values

```python
def parse_name(full_name: str) -> tuple[str, str]:
    """Split a full name into first and last name.

    Args:
        full_name: Full name in "First Last" format

    Returns:
        Tuple of (first_name, last_name)

    Example:
        >>> first, last = parse_name("John Doe")
        >>> print(first)
        John
    """
```

### Generator Functions

```python
def read_lines(filepath: str) -> Generator[str, None, None]:
    """Yield lines from a file one at a time.

    Args:
        filepath: Path to the text file

    Yields:
        Each line from the file with trailing newline removed

    Example:
        >>> for line in read_lines("data.txt"):
        ...     print(line)
    """
```

### Context Managers

```python
class FileManager:
    """Manage file operations with automatic cleanup.

    This context manager ensures files are properly closed
    even if exceptions occur.

    Example:
        >>> with FileManager("data.txt") as f:
        ...     data = f.read()
    """
```

## Output Format

When documenting code, provide:

1. The complete docstring formatted with proper indentation
2. Ready to insert directly into the function/class
3. Using the requested style (or Google style by default)

**Example output:**

```python
    """Calculate the sum of squares of a list of numbers.

    Args:
        numbers: List of numeric values

    Returns:
        Sum of the squares of all numbers in the list

    Raises:
        ValueError: If the list is empty

    Example:
        >>> sum_of_squares([1, 2, 3])
        14
    """
```

Notice the indentation matches what would appear in a function body.
