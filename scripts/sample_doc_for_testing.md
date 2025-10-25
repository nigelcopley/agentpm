# Sample Documentation with Code Examples

## Example 1: Basic Python (Should Pass)

This example demonstrates basic Python operations:

```python
# Simple arithmetic
result = 2 + 2
assert result == 4, "Math is broken!"

# String operations
greeting = "Hello, World!"
assert len(greeting) > 0, "String should not be empty"
```

## Example 2: Working with Lists (Should Pass)

```python
# List operations
numbers = [1, 2, 3, 4, 5]
doubled = [n * 2 for n in numbers]
assert doubled == [2, 4, 6, 8, 10], "List comprehension failed"
```

## Example 3: Intentional Failure (Should Fail)

This example intentionally fails to demonstrate test detection:

```python
# This will fail!
result = 2 + 2
assert result == 5, "This assertion will fail - 2+2 != 5"
```

## Example 4: Import Test (Should Pass)

```python
# Test that standard library imports work
import os
import sys
from pathlib import Path

assert hasattr(os, 'path'), "os module should have path"
assert hasattr(sys, 'version'), "sys module should have version"
```
