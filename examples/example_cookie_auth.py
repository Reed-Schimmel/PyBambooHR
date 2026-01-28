#!/usr/bin/env python
# encoding:utf-8
"""
Example: Using PyBambooHR with Okta SSO Cookie Authentication

This example demonstrates how to use PyBambooHR with browser cookies
extracted from Chrome after logging in via Okta SSO.
"""

from PyBambooHR import PyBambooHR

# ============================================================================
# HOW TO GET YOUR COOKIES:
# ============================================================================
# 1. Open Chrome and log into BambooHR via your Okta dashboard
# 2. Complete 2FA if prompted
# 3. Press F12 to open Chrome DevTools
# 4. Go to Network tab
# 5. Refresh the BambooHR page (Cmd+R or Ctrl+R)
# 6. Click any request to actian.bamboohr.com
# 7. Scroll down to "Request Headers"
# 8. Find the "Cookie:" header
# 9. Copy everything AFTER "Cookie: "
# 10. Paste below
# ============================================================================

# Example cookie string (replace with your actual cookies)
cookies = (
    "PHPSESSID=your_session_id_here; "
    "trusted_browser=your_token_here; "
    "lluidt=your_lluidt_here; "
    "lluidh=your_lluidh_here; "
    "lluid=your_lluid_here; "
    "llfn=your_name; "
    "llcid=your_cid; "
    "bhr_features=features; "
    "acceptCookies=true; "
    "_dd_s=logs; "
    "_cfuvid=cloudflare_id"
)

# Initialize PyBambooHR with cookie authentication
bamboo = PyBambooHR(
    subdomain="actian",  # Replace with your company subdomain
    auth_method="cookies",
    cookies=cookies,
)

# ============================================================================
# Now use PyBambooHR normally - all API methods work with cookie auth
# ============================================================================

try:
    # Get employee directory
    print("Fetching employee directory...")
    employees = bamboo.get_employee_directory()
    print("Found {} employees".format(len(employees)))

    # Get specific employee
    if employees:
        first_employee_id = employees[0]["id"]
        print("\nFetching employee {}...".format(first_employee_id))
        employee = bamboo.get_employee(
            first_employee_id, ["firstName", "lastName", "workEmail", "department"]
        )
        print("Employee: {firstName} {lastName}".format(**employee))

    # Request a report
    print("\nRequesting company report...")
    report = bamboo.request_company_report(1, report_format="json")
    print("Report retrieved successfully")

except Exception as e:
    print("\nError: {}".format(e))
    print(
        "\nIf you see a cookie expiration error, follow the prompts to paste fresh cookies."
    )

# ============================================================================
# ALTERNATIVE: Use cookie file
# ============================================================================

# Save cookies to a file (do this once)
# with open('bamboohr_cookies.txt', 'w') as f:
#     f.write(cookies)

# Then use the file:
# bamboo = PyBambooHR(
#     subdomain='actian',
#     auth_method='cookies',
#     cookie_file='bamboohr_cookies.txt'
# )

# ============================================================================
# ALTERNATIVE: Use dictionary format
# ============================================================================

# cookies_dict = {
#     'PHPSESSID': 'your_session_id',
#     'trusted_browser': 'your_token',
#     'lluidt': 'your_lluidt',
#     # ... add all other cookies
# }
#
# bamboo = PyBambooHR(
#     subdomain='actian',
#     auth_method='cookies',
#     cookies=cookies_dict
# )

# ============================================================================
# MANUAL COOKIE REFRESH
# ============================================================================

# If you want to manually refresh cookies instead of using the automatic prompt:
# new_cookies = "PHPSESSID=new_session_id; trusted_browser=new_token; ..."
# bamboo.refresh_cookies(cookies=new_cookies)

print("\n" + "=" * 60)
print("Example completed successfully!")
print("=" * 60)
