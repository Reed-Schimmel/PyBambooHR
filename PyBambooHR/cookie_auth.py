#!/usr/bin/env python
# encoding:utf-8
# project:PyBambooHR
# repository:http://github.com/smeggingsmegger/PyBambooHR
# license:mit (http://opensource.org/licenses/MIT)

"""
Cookie authentication module for PyBambooHR.

This module provides support for authenticating with BambooHR using browser
session cookies, which is useful for users who access BambooHR via SSO
providers like Okta.

Usage:
    from PyBambooHR.cookie_auth import parse_cookies, create_session_from_cookies

    # Parse cookie string from browser
    cookies = parse_cookies("PHPSESSID=abc123; trusted_browser=xyz")

    # Create session with cookies
    session = create_session_from_cookies(cookies, 'yourcompany')
"""

import json
import requests

# Python 2/3 compatibility
try:
    basestring
except NameError:
    basestring = str


class CookieAuthException(Exception):
    """Base exception for cookie authentication errors."""

    pass


class CookieExpiredException(CookieAuthException):
    """Raised when session cookies have expired (401/403 response)."""

    pass


class CookieParseException(CookieAuthException):
    """Raised when cookie parsing fails."""

    pass


def parse_cookie_header(cookie_string):
    """
    Parse cookie string from browser DevTools Network tab "Cookie:" header.

    Input format: "PHPSESSID=abc123; trusted_browser=xyz; lluidt=token456"
    Output: {'PHPSESSID': 'abc123', 'trusted_browser': 'xyz', 'lluidt': 'token456'}

    @param cookie_string: String from "Cookie:" header in DevTools
    @return: Dictionary of cookie name-value pairs
    @raises CookieParseException: If cookie string is invalid
    """
    if not cookie_string or not isinstance(cookie_string, basestring):
        raise CookieParseException("Cookie string must be a non-empty string")

    # Remove "Cookie: " prefix if present
    cookie_string = cookie_string.strip()
    if cookie_string.lower().startswith("cookie:"):
        cookie_string = cookie_string[7:].strip()

    cookies = {}

    # Split by semicolon and parse each cookie
    for part in cookie_string.split(";"):
        part = part.strip()
        if not part:
            continue

        # Split on first '=' only (value may contain '=')
        if "=" not in part:
            continue  # Skip malformed cookies

        name, value = part.split("=", 1)
        name = name.strip()
        value = value.strip()

        if name:
            cookies[name] = value

    if not cookies:
        raise CookieParseException(
            "No valid cookies found in string. Expected format: "
            "'name1=value1; name2=value2'"
        )

    return cookies


def parse_cookie_dict(cookie_dict):
    """
    Validate and normalize a Python dictionary of cookies.

    @param cookie_dict: Dictionary of cookie names and values
    @return: Validated dictionary
    @raises CookieParseException: If dictionary is empty or invalid
    """
    if not cookie_dict:
        raise CookieParseException("Cookie dictionary cannot be empty")

    if not isinstance(cookie_dict, dict):
        raise CookieParseException(
            "Expected dictionary, got {}".format(type(cookie_dict).__name__)
        )

    # Validate all keys and values are strings
    validated = {}
    for name, value in cookie_dict.items():
        if not isinstance(name, basestring):
            raise CookieParseException(
                "Cookie name must be string, got {}".format(type(name).__name__)
            )

        # Convert value to string if needed
        validated[str(name)] = str(value) if value is not None else ""

    return validated


def parse_cookie_json(cookie_json):
    """
    Parse JSON from browser extensions (Cookie-Editor, EditThisCookie).

    Supports formats:
    - Array of objects: [{"name": "PHPSESSID", "value": "abc123"}, ...]
    - Object with cookies: {"PHPSESSID": "abc123", ...}

    @param cookie_json: JSON string or already-parsed list/dict
    @return: Dictionary of cookie name-value pairs
    @raises CookieParseException: If JSON is invalid or in unexpected format
    """
    # Parse JSON string if needed
    if isinstance(cookie_json, basestring):
        try:
            data = json.loads(cookie_json)
        except (ValueError, TypeError) as e:
            raise CookieParseException("Invalid JSON: {}".format(str(e)))
    else:
        data = cookie_json

    # Handle array of cookie objects (most common export format)
    if isinstance(data, list):
        cookies = {}
        for item in data:
            if isinstance(item, dict):
                name = item.get("name")
                value = item.get("value", "")
                if name:
                    cookies[str(name)] = str(value) if value is not None else ""

        if not cookies:
            raise CookieParseException(
                "No valid cookies found in JSON array. Expected format: "
                '[{"name": "PHPSESSID", "value": "abc123"}, ...]'
            )
        return cookies

    # Handle plain object
    if isinstance(data, dict):
        return parse_cookie_dict(data)

    raise CookieParseException(
        "Unexpected JSON format. Expected array or object, got {}".format(
            type(data).__name__
        )
    )


def detect_cookie_format(cookies):
    """
    Auto-detect which format the cookies are in.

    @param cookies: String, dict, or list
    @return: 'header', 'dict', or 'json'
    @raises CookieParseException: If format cannot be determined
    """
    if cookies is None:
        raise CookieParseException("Cookies cannot be None")

    # Dictionary format
    if isinstance(cookies, dict):
        return "dict"

    # List format (JSON array)
    if isinstance(cookies, list):
        return "json"

    # String format - check if JSON or header
    if isinstance(cookies, basestring):
        stripped = cookies.strip()

        # Check for JSON array
        if stripped.startswith("["):
            return "json"

        # Check for JSON object
        if stripped.startswith("{"):
            return "json"

        # Assume header format (name=value; name=value)
        return "header"

    raise CookieParseException(
        "Cannot detect cookie format. Expected string, dict, or list, got {}".format(
            type(cookies).__name__
        )
    )


def parse_cookies(cookies):
    """
    Main entry point - automatically detects format and parses cookies.

    Supports:
    - Header string: "PHPSESSID=abc123; trusted_browser=xyz"
    - Python dict: {'PHPSESSID': 'abc123', 'trusted_browser': 'xyz'}
    - JSON array: '[{"name": "PHPSESSID", "value": "abc123"}, ...]'
    - JSON object: '{"PHPSESSID": "abc123", ...}'

    @param cookies: Any supported format (string, dict, JSON)
    @return: Dictionary of cookie name-value pairs
    @raises CookieParseException: If format is invalid or cookies are empty
    """
    if not cookies:
        raise CookieParseException("Cookies cannot be empty")

    fmt = detect_cookie_format(cookies)

    if fmt == "header":
        return parse_cookie_header(cookies)
    elif fmt == "dict":
        return parse_cookie_dict(cookies)
    elif fmt == "json":
        return parse_cookie_json(cookies)
    else:
        raise CookieParseException("Unknown cookie format: {}".format(fmt))


def create_session_from_cookies(cookies, subdomain):
    """
    Create a requests.Session with cookies configured for BambooHR.

    @param cookies: Parsed cookie dictionary (name: value pairs)
    @param subdomain: BambooHR subdomain (e.g., 'actian' for actian.bamboohr.com)
    @return: requests.Session object configured with cookies
    """
    if not isinstance(cookies, dict):
        raise CookieParseException("Cookies must be a dictionary")

    if not subdomain:
        raise ValueError("Subdomain is required")

    session = requests.Session()

    # Set cookies for both the main domain and API domain
    domains = [
        ".bamboohr.com",
        "{}.bamboohr.com".format(subdomain),
        "api.bamboohr.com",
    ]

    for name, value in cookies.items():
        for domain in domains:
            session.cookies.set(name, value, domain=domain)

    return session


def prompt_for_cookies():
    """
    Interactive prompt for user to provide fresh cookies.

    @return: Cookie string entered by user
    @raises KeyboardInterrupt: If user cancels
    """
    # Python 2/3 compatible input
    try:
        input_func = raw_input  # Python 2
    except NameError:
        input_func = input  # Python 3

    print("\n" + "=" * 60)
    print("SESSION EXPIRED - Fresh cookies needed")
    print("=" * 60)
    print("\nYour BambooHR session has expired.")
    print("\nTo continue:")
    print("1. Open Chrome and log into BambooHR via Okta")
    print("2. Press F12 -> Network tab")
    print("3. Refresh page, click any request to bamboohr.com")
    print("4. Find 'Cookie:' header in Request Headers and copy the value")
    print("5. Paste below")
    print("\nExample format:")
    print("PHPSESSID=abc123; trusted_browser=xyz; lluidt=token456")
    print("-" * 60)

    new_cookies = input_func("\nPaste cookies here: ").strip()

    if not new_cookies:
        raise CookieParseException("No cookies provided")

    return new_cookies
