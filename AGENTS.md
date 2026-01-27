# PyBambooHR Agent Guidelines

This document provides guidelines for AI coding agents working in the PyBambooHR repository.

## Project Overview

PyBambooHR is a Python API wrapper for BambooHR. It focuses on managing employee information and supports Python 2.7+ and Python 3.x. The project uses the `requests` library for HTTP calls and `httpretty` for mocking in tests.

## Build, Lint, and Test Commands

### Running Tests

```bash
# Run all tests
nosetests

# Run a specific test file
nosetests tests/test_employees.py

# Run a specific test class
nosetests tests/test_employees.py:test_employees

# Run a specific test method
nosetests tests/test_employees.py:test_employees.test_get_employee_directory
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Building and Distribution

```bash
# Build distribution packages
python setup.py sdist

# Upload to PyPI (requires credentials)
python pypi.py
```

## Project Structure

```
PyBambooHR/
├── PyBambooHR/          # Main package directory
│   ├── __init__.py      # Package exports
│   ├── PyBambooHR.py    # Main API class
│   ├── utils.py         # Utility functions
│   └── config.py        # Configuration defaults
├── tests/               # Test suite
│   ├── test_employees.py
│   ├── test_misc.py
│   └── test_reports.py
├── setup.py            # Package setup
└── requirements.txt    # Dependencies
```

## Code Style Guidelines

### Python Compatibility

- Code must support both Python 2.7 and Python 3.x
- Use compatibility patterns for `basestring`, `unicode`, and `bytes`
- Example compatibility pattern:
  ```python
  try:
      basestring
  except NameError:
      basestring = str
  ```

### Import Style

- Standard library imports first
- Third-party imports second
- Local/relative imports last
- Use relative imports within the package: `from . import utils`
- Example from PyBambooHR.py:
  ```python
  import datetime
  import requests
  from . import utils
  from . import config
  from .utils import make_field_xml
  from os.path import basename
  ```

### Naming Conventions

- **Classes**: PascalCase (e.g., `PyBambooHR`)
- **Functions/Methods**: snake_case (e.g., `get_employee`, `add_employee`)
- **Private methods**: Prefix with underscore (e.g., `_format_employee_xml`, `_parse_xml`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `XML_ESCAPES`)
- **Variables**: snake_case (e.g., `employee_fields`, `api_key`)

### Docstrings

- Use triple-quoted strings for docstrings
- Document parameters with `@param` notation
- Include purpose and return information
- Example:
  ```python
  def get_employee(self, employee_id, fields=None):
      """
      Get employee information by employee ID.
      
      @param employee_id: The numerical employee ID
      @param fields: Optional list of field names to retrieve
      """
  ```

### File Headers

All Python files should include a header:
```python
#!/usr/bin/env python
#encoding:utf-8
#author:smeggingsmegger/Scott Blevins
#project:PyBambooHR
#repository:http://github.com/smeggingsmegger/PyBambooHR
#license:mit (http://opensource.org/licenses/MIT)
```

### Formatting

- Use 4 spaces for indentation (no tabs)
- Maximum line length: ~100 characters (flexible)
- Single blank line between methods
- Two blank lines between classes and top-level functions

### Type Handling

- Validate input types before processing
- Convert types explicitly when needed
- Use `isinstance()` for type checking
- Example:
  ```python
  if isinstance(arg, (datetime.datetime, datetime.date)):
      return arg.strftime('%Y-%m-%d')
  ```

### Error Handling

- Raise `HTTPError` for HTTP-related failures
- Raise `UserWarning` for invalid user input
- Raise `ValueError` for invalid argument values
- Raise `NotImplemented` for unsupported features
- Example:
  ```python
  if not employee or 'firstName' not in employee:
      raise UserWarning("Missing required field: firstName")
  ```

### String Formatting

- Use `.format()` for string formatting (Python 2/3 compatibility)
- XML escaping required for user input in XML context
- Use the `escape()` utility for XML values

## Testing Guidelines

### Test Structure

- Test files named `test_*.py`
- Test classes inherit from `unittest.TestCase`
- Test methods prefixed with `test_`
- Use `httpretty.activate` decorator for HTTP mocking

### Test Setup

```python
class test_employees(unittest.TestCase):
    bamboo = None
    
    def setUp(self):
        if self.bamboo is None:
            self.bamboo = PyBambooHR(subdomain='test', api_key='testingnotrealapikey')
```

### Mocking HTTP Requests

```python
@httpretty.activate
def test_get_employee(self):
    httpretty.register_uri(
        httpretty.GET, 
        "https://api.bamboohr.com/api/gateway.php/test/v1/employees/123",
        body='{"firstName": "John"}',
        status=200
    )
    result = self.bamboo.get_employee(123)
```

## Common Patterns

### API Request Structure

- Base URL: `https://api.bamboohr.com/api/gateway.php/{subdomain}/v1/`
- Authentication: Basic auth with API key as username, empty password
- Headers: `{'Accept': 'application/json'}`
- Timeout: 60 seconds default

### Data Transformation

- Convert camelCase to snake_case when `underscore_keys=True`
- Use utility functions: `camelcase_to_underscore()`, `underscore_to_camelcase()`
- Transform XML to dict using `xmltodict.parse()`

### Employee Data Fields

Reference `self.employee_fields` dict in PyBambooHR class for valid field names and types.

## Notes

- This is a discontinued project (as of README note)
- Focus on Python 2.7 compatibility while supporting Python 3.x
- BambooHR API documentation: http://www.bamboohr.com/api/documentation/
