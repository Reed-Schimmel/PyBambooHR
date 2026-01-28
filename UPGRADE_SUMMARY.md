# PyBambooHR v0.9.0 - Upgrade Summary

## Project Maintainership Transfer

**Previous Maintainer:** Scott Blevins (smeggingsmegger)  
**New Maintainer:** Reed Schimmel (Reed-Schimmel)  
**Release Date:** January 27, 2025  
**Version:** 0.9.0 (upgraded from 0.8.1)

---

## Major Changes

### 1. Cookie Authentication for SSO Users

The most significant addition is full support for browser session cookie authentication, enabling users who authenticate via Okta SSO (or other SSO providers) to use PyBambooHR without needing API keys.

**Key Features:**
- Extract cookies from Chrome DevTools after Okta login
- Support for multiple cookie input formats (string, dict, JSON, file)
- Automatic cookie expiration detection
- Interactive cookie refresh with step-by-step guide
- No additional dependencies required

**Example Usage:**
```python
from PyBambooHR import PyBambooHR

# After logging into BambooHR via Okta in Chrome
cookies = "PHPSESSID=session_id; trusted_browser=token; lluidt=..."

bamboo = PyBambooHR(
    subdomain='yourcompany',
    auth_method='cookies',
    cookies=cookies
)

employees = bamboo.get_employee_directory()
```

### 2. Python 3 Improvements

- Fixed Python 3 compatibility issues (`iteritems()` → `items()`)
- Fixed package imports for Python 3
- Added explicit Python 3.6-3.11 support
- Maintained backward compatibility with Python 2.7

### 3. Enhanced Testing

- Added 38 new test cases for cookie authentication
- All 63 tests passing (38 new + 25 existing)
- Comprehensive test coverage for:
  - Cookie parsing (header, dict, JSON formats)
  - Session management
  - Cookie expiration handling
  - Backward compatibility

---

## Files Created

1. **PyBambooHR/cookie_auth.py** (new, 330 lines)
   - Cookie parsing functions
   - Session management
   - Custom exceptions (CookieAuthException, CookieExpiredException, CookieParseException)
   - Interactive cookie refresh prompt

2. **tests/test_cookie_auth.py** (new, 418 lines)
   - 38 comprehensive test cases
   - Tests for all cookie formats
   - Integration tests with PyBambooHR class
   - Cookie expiration tests

3. **UPGRADE_SUMMARY.md** (this file)
   - Documentation of changes and upgrade path

---

## Files Modified

1. **PyBambooHR/PyBambooHR.py**
   - Added `auth_method`, `cookies`, `cookie_file` parameters
   - New `_make_request()` unified request method
   - New `refresh_cookies()` method
   - New `_handle_cookie_expiration()` method
   - Updated all 19 HTTP request locations
   - Fixed `iteritems()` → `items()` for Python 3

2. **PyBambooHR/__init__.py**
   - Fixed imports for Python 3 compatibility
   - Exported cookie authentication classes

3. **PyBambooHR/config.py**
   - Added `auth_method` configuration option
   - Added `cookie_file` configuration option

4. **README.md**
   - Added maintainer transfer notice
   - Added "What's New in v0.9.0" section
   - Added comprehensive cookie authentication guide
   - Added Chrome cookie extraction instructions
   - Added cookie format examples
   - Added security notes

5. **CHANGES**
   - Added v0.9.0 release notes
   - Documented all new features and improvements
   - Listed new modules and tests

6. **setup.py**
   - Bumped version: 0.8.1 → 0.9.0
   - Updated maintainer information
   - Updated repository URL
   - Updated description
   - Added SSO/Okta/Cookie keywords
   - Updated development status: Alpha → Beta
   - Added Python 3.6-3.11 classifiers

---

## Backward Compatibility

**100% backward compatible** - All existing code using API key authentication continues to work without any changes:

```python
# This still works exactly as before
bamboo = PyBambooHR(subdomain='yourcompany', api_key='your_api_key')
employees = bamboo.get_employee_directory()
```

Default `auth_method` is `'api_key'`, so existing code doesn't need modification.

---

## API Changes

### New Parameters

**PyBambooHR.__init__()**
- `auth_method` (str, default='api_key'): Authentication method - 'api_key' or 'cookies'
- `cookies` (str|dict|list, optional): Browser cookies for authentication
- `cookie_file` (str, optional): Path to file containing cookies

### New Methods

**PyBambooHR.refresh_cookies(cookies=None, cookie_file=None)**
- Update expired session cookies
- Raises `RuntimeError` if not using cookie authentication

**PyBambooHR._make_request(method, url, auto_refresh=True, **kwargs)**
- Internal: Unified HTTP request handler
- Automatically handles both authentication methods
- Detects cookie expiration and prompts for refresh

**PyBambooHR._handle_cookie_expiration()**
- Internal: Interactive prompt for fresh cookies
- Called automatically when cookies expire

### New Exceptions

**From PyBambooHR.cookie_auth:**
- `CookieAuthException`: Base exception for cookie auth errors
- `CookieExpiredException`: Raised when session cookies expire
- `CookieParseException`: Raised when cookie parsing fails

---

## Testing

All tests pass successfully:

```bash
$ python -m unittest discover tests -v
Ran 63 tests in 0.032s
OK
```

**Test Breakdown:**
- Cookie parsing tests: 20
- Cookie authentication integration tests: 10
- Cookie expiration tests: 8
- Existing employee tests: 13
- Existing misc tests: 8
- Existing report tests: 4

---

## Installation

### From Source
```bash
git clone https://github.com/Reed-Schimmel/PyBambooHR.git
cd PyBambooHR
pip install -e .
```

### From PyPI (when published)
```bash
pip install PyBambooHR==0.9.0
```

---

## Usage Guide

### For API Key Users (Existing)
No changes required. Continue using as before:

```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yourcompany', api_key='your_api_key')
employee = bamboo.get_employee(123)
```

### For Okta SSO Users (New)

1. **Log into BambooHR via Okta** in Chrome
2. **Open DevTools** (F12) → Network tab
3. **Refresh page**, click any request to `yourcompany.bamboohr.com`
4. **Copy the Cookie header** from Request Headers
5. **Use in your script:**

```python
from PyBambooHR import PyBambooHR

cookies = "PHPSESSID=abc123; trusted_browser=xyz; lluidt=token456"

bamboo = PyBambooHR(
    subdomain='yourcompany',
    auth_method='cookies',
    cookies=cookies
)

# When cookies expire, you'll be prompted automatically:
employees = bamboo.get_employee_directory()
```

---

## Security Considerations

- Cookies provide full account access - treat them like passwords
- Never commit cookie files to version control
- Add `*.cookies`, `cookies.txt`, etc. to `.gitignore`
- Use file permissions (chmod 600) for cookie files on Unix systems
- Cookies typically expire after 24 hours or logout
- The library prompts for fresh cookies when they expire

---

## Known Issues / Limitations

1. **Cookie identification**: The minimum required set of cookies hasn't been definitively identified. The library captures all cookies, and users may need to experiment to find which specific cookies (like PHPSESSID) are actually required.

2. **Session duration**: Cookie lifetime depends on BambooHR's session configuration and may vary by organization.

3. **Python 2.7**: While still supported, Python 2 reached end-of-life in 2020. Consider migrating to Python 3.6+.

---

## Future Roadmap

Potential enhancements for future versions:
- Automatic cookie persistence and refresh
- Support for other SSO providers (Azure AD, Google Workspace, etc.)
- Browser automation for fully automatic cookie extraction
- Token-based authentication if BambooHR adds OAuth support
- Async/await support for Python 3.7+

---

## Credits

**Original Author:** Scott Blevins (smeggingsmegger)  
**New Maintainer:** Reed Schimmel (Reed-Schimmel)  
**Contributors:** Ng Zhi An, and others from the original project

**Special Thanks:**
- Scott Blevins for creating the original PyBambooHR library
- The BambooHR team for their API
- The requests and httpretty library maintainers

---

## License

MIT License - See LICENSE file for details

Copyright (c) 2013-2022 Scott Blevins  
Copyright (c) 2025 Reed Schimmel

---

## Support
- This was vibe coded with human verification, idk how to help you :-)

For issues, questions, or contributions:
- GitHub Issues: https://github.com/Reed-Schimmel/PyBambooHR/issues
- GitHub Discussions: https://github.com/Reed-Schimmel/PyBambooHR/discussions

---

**Last Updated:** January 27, 2025  
**Document Version:** 1.0
