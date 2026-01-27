# PyBambooHR

**Original project discontinued by [smeggingsmegger](https://github.com/smeggingsmegger/PyBambooHR)**  
**New version maintained by [Reed-Schimmel](https://github.com/Reed-Schimmel)**

---

## Important Notice

The original PyBambooHR project was created and maintained by Scott Blevins (GitHub user smeggingsmegger). Scott discontinued the project as he no longer had access to BambooHR and moved on from the company that required it.

This fork by Reed-Schimmel adds **SSO/Cookie authentication support for Okta users** while maintaining full backward compatibility with the original API.

---

[![Build Status](https://secure.travis-ci.org/smeggingsmegger/PyBambooHR.png)](https://travis-ci.org/smeggingsmegger/PyBambooHR)&nbsp;&nbsp;&nbsp;![Download Stats](https://pypip.in/download/PyBambooHR/badge.svg)

This is an unofficial Python API for Bamboo HR. So far it is focusing on managing employee information but you can pretty much do anything you want with a little python.

The library makes use of the [requests](http://docs.python-requests.org/en/latest/) library for Python and [HTTPretty](https://github.com/gabrielfalcao/HTTPretty) for testing. A huge thank you to both of those excellent projects.

## What's New in v0.9.0

- **Cookie Authentication for SSO Users** - Authenticate using browser session cookies (perfect for Okta SSO users)
- **Interactive Cookie Refresh** - Automatic prompts when cookies expire with step-by-step Chrome extraction guide
- **100% Backward Compatible** - All existing API key authentication code works unchanged
- **38 New Tests** - Comprehensive test coverage for cookie authentication
- **Better Documentation** - Detailed guides for both authentication methods

## Installation

```bash
pip install git+https://github.com/Reed-Schimmel/PyBambooHR.git@master
```

## Authentication Methods

PyBambooHR supports two authentication methods:

### 1. API Key Authentication (Default)

Using this library is very simple:

```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yoursub', api_key='yourapikeyhere')

employees = bamboo.get_employee_directory()
```

(Note that you have to enable sharing employee directory to use that method.)

### 2. Cookie Authentication (for Okta SSO users)

If your company uses Okta SSO (or another SSO provider) to access BambooHR, you can authenticate using browser session cookies instead of an API key.

#### Quick Start

```python
from PyBambooHR import PyBambooHR

# Extract cookies from Chrome after logging into BambooHR via Okta
cookies = "PHPSESSID=your_session_id; trusted_browser=your_token; lluidt=your_lluidt"

bamboo = PyBambooHR(
    subdomain='yourcompany',
    auth_method='cookies',
    cookies=cookies
)

# Use normally
employees = bamboo.get_employee_directory()
```

#### How to Extract Cookies from Chrome

1. **Log into BambooHR** via your Okta dashboard (complete 2FA if prompted)

2. **Open Chrome DevTools** (Press `F12` or `Cmd+Option+I` on Mac)

3. **Go to Network tab**
   - Refresh the page (`Cmd+R` or `Ctrl+R`)
   - Click any request to `yourcompany.bamboohr.com`

4. **Copy Cookie header**
   - Scroll down to "Request Headers" section
   - Find the `Cookie:` header
   - Copy everything after "Cookie: "

5. **Use in your script** - paste the copied string as the `cookies` parameter

**Example Cookie String:**
```
PHPSESSID=abc123def456; trusted_browser=xyz789; lluidt=token123; lluidh=hash456; lluid=uid789; llfn=John; llcid=cid123; bhr_features=feat1; acceptCookies=true; _dd_s=logs; _cfuvid=cf123
```

#### Cookie Input Formats

PyBambooHR supports multiple cookie formats:

**Header string format (Recommended):**
```python
cookies = "PHPSESSID=abc123; trusted_browser=xyz"
```

**Python dictionary:**
```python
cookies = {'PHPSESSID': 'abc123', 'trusted_browser': 'xyz'}
```

**JSON array (from browser extensions like Cookie-Editor):**
```python
cookies = '[{"name": "PHPSESSID", "value": "abc123"}, {"name": "trusted_browser", "value": "xyz"}]'
```

**Cookie file:**
```python
# Save cookies to file: cookies.txt
bamboo = PyBambooHR(
    subdomain='yourcompany',
    auth_method='cookies',
    cookie_file='cookies.txt'
)
```

**Important:** Add cookie files to `.gitignore` - never commit cookies!

#### Handling Cookie Expiration

Cookies typically expire after 24 hours or when you log out. When they expire, PyBambooHR will automatically prompt you for fresh cookies:

```
============================================================
SESSION EXPIRED - Fresh cookies needed
============================================================

Your BambooHR session has expired.

To continue:
1. Open Chrome and log into BambooHR via Okta
2. Press F12 -> Network tab
3. Refresh page, click any request to bamboohr.com
4. Find 'Cookie:' header in Request Headers and copy the value
5. Paste below

Example format:
PHPSESSID=abc123; trusted_browser=xyz; lluidt=token456
------------------------------------------------------------

Paste cookies here: _
```

You can also manually refresh cookies:

```python
# When you notice cookies have expired
new_cookies = "PHPSESSID=new_session; trusted_browser=new_token"
bamboo.refresh_cookies(cookies=new_cookies)
```

#### Required Cookies

The minimum required cookies may vary. We recommend including all cookies for best compatibility:

- `PHPSESSID` - PHP session ID (likely required)
- `trusted_browser` - Browser trust token
- `lluidt`, `lluidh`, `lluid`, `llfn`, `llcid` - User identification
- `bhr_features`, `acceptCookies` - Feature flags
- `_dd_s` - Datadog analytics (probably optional)
- `_cfuvid` - Cloudflare verification (probably optional)

Start with just `PHPSESSID` first, and add others if you get authentication errors.

#### Security Notes

- Cookies provide full access to your BambooHR account
- Never commit cookie files to version control
- Don't share cookies with others
- Store cookie files with restricted permissions (chmod 600 on Unix)
- Cookies expire automatically, reducing long-term risk

---

## API Examples

This will give you a list of employees with properties on each including their ID.


```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yoursub', api_key='yourapikeyhere')

# Jim's employee ID is 123 and we are not specifying fields so this will get all of them.
jim = bamboo.get_employee(123)

# Pam's employee ID is 222 and we are specifying fields so this will get only the ones we request.
pam = bamboo.get_employee(222, ['city', 'workPhone', 'workEmail'])

```

Adding an employee

```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yoursub', api_key='yourapikeyhere')

# The firstName and lastName keys are required...
employee = {'firstName': 'Test', 'lastName': 'Person'}

result = bamboo.add_employee(employee)

The result dict will contain id and location. "id" is the numerical BambooHR employee ID. Location is a link to that employee.

```

Updating an employee

```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yoursub', api_key='yourapikeyhere')

# His name was test person...
employee = {'firstName': 'Another', 'lastName': 'Namenow'}

# Use the ID and then the dict with the new information
result = bamboo.update_employee(333, employee)

result will be True or False depending on if it succeeded.

```

Requesting a Report

```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yoursub', api_key='yourapikeyhere')

# Use the ID to request json information
result = bamboo.request_company_report(1, format='json', filter_duplicates=True)

# Now do stuff with your results (Will vary by report.)
for employee in result['employees']:
    print(employee)

# Use the ID and save a pdf:
result = bamboo.request_company_report(1, format='pdf', output_file='/tmp/report.pdf', filter_duplicates=True)

```
Getting information that is scheduled in the future
```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yoursub', api_key='yourapikeyhere', only_current=False)

```
BambooHR has effective dates for when promotions are scheduled to happen or when new hires are going to join the organization. In order to see these events before they happen using the BambooHR API set `only_current` to `False`. As a note, this only works for pulling reports and getting employee information. This does not work on getting the employee directory.
