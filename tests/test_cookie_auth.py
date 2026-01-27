#!/usr/bin/env python
# encoding:utf-8
# project:PyBambooHR
# repository:http://github.com/smeggingsmegger/PyBambooHR
# license:mit (http://opensource.org/licenses/MIT)

"""Unit tests for cookie authentication"""

import httpretty
import os
import sys
import unittest

# Force parent directory onto path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyBambooHR.cookie_auth import (
    parse_cookie_header,
    parse_cookie_dict,
    parse_cookie_json,
    detect_cookie_format,
    parse_cookies,
    create_session_from_cookies,
    CookieAuthException,
    CookieExpiredException,
    CookieParseException,
)
from PyBambooHR.PyBambooHR import PyBambooHR


class TestCookieParsing(unittest.TestCase):
    """Test cookie parsing functions"""

    def test_parse_cookie_header_basic(self):
        """Test parsing basic cookie header string"""
        cookie_str = "PHPSESSID=abc123; trusted_browser=xyz"
        result = parse_cookie_header(cookie_str)
        self.assertEqual(result["PHPSESSID"], "abc123")
        self.assertEqual(result["trusted_browser"], "xyz")

    def test_parse_cookie_header_complex(self):
        """Test parsing all BambooHR cookies"""
        cookie_str = (
            "PHPSESSID=abc123; trusted_browser=xyz; lluidt=token456; "
            "lluidh=hash789; lluid=uid123; llfn=firstname; llcid=cid456; "
            "bhr_features=feat1; acceptCookies=true; _dd_s=logs; _cfuvid=cf123"
        )
        result = parse_cookie_header(cookie_str)
        self.assertEqual(len(result), 11)
        self.assertEqual(result["PHPSESSID"], "abc123")
        self.assertEqual(result["_cfuvid"], "cf123")

    def test_parse_cookie_header_with_spaces(self):
        """Test parsing with extra spaces"""
        cookie_str = "PHPSESSID=abc123;  trusted_browser=xyz  ; lluidt=token456"
        result = parse_cookie_header(cookie_str)
        self.assertEqual(result["PHPSESSID"], "abc123")
        self.assertEqual(result["trusted_browser"], "xyz")
        self.assertEqual(result["lluidt"], "token456")

    def test_parse_cookie_header_with_prefix(self):
        """Test parsing with 'Cookie:' prefix (as copied from DevTools)"""
        cookie_str = "Cookie: PHPSESSID=abc123; trusted_browser=xyz"
        result = parse_cookie_header(cookie_str)
        self.assertEqual(result["PHPSESSID"], "abc123")
        self.assertEqual(result["trusted_browser"], "xyz")

    def test_parse_cookie_header_with_equals_in_value(self):
        """Test parsing cookie value containing equals sign"""
        cookie_str = "token=abc=123=xyz; other=value"
        result = parse_cookie_header(cookie_str)
        self.assertEqual(result["token"], "abc=123=xyz")
        self.assertEqual(result["other"], "value")

    def test_parse_cookie_header_empty_raises(self):
        """Test that empty string raises exception"""
        with self.assertRaises(CookieParseException):
            parse_cookie_header("")

    def test_parse_cookie_header_none_raises(self):
        """Test that None raises exception"""
        with self.assertRaises(CookieParseException):
            parse_cookie_header(None)

    def test_parse_cookie_dict(self):
        """Test parsing dictionary format"""
        cookie_dict = {"PHPSESSID": "abc123", "trusted_browser": "xyz"}
        result = parse_cookie_dict(cookie_dict)
        self.assertEqual(result, cookie_dict)

    def test_parse_cookie_dict_converts_types(self):
        """Test that dict values are converted to strings"""
        cookie_dict = {"int_val": 123, "bool_val": True}
        result = parse_cookie_dict(cookie_dict)
        self.assertEqual(result["int_val"], "123")
        self.assertEqual(result["bool_val"], "True")

    def test_parse_cookie_dict_empty_raises(self):
        """Test that empty dict raises exception"""
        with self.assertRaises(CookieParseException):
            parse_cookie_dict({})

    def test_parse_cookie_json_array(self):
        """Test parsing JSON array from browser extensions"""
        cookie_json = """[
            {"name": "PHPSESSID", "value": "abc123"},
            {"name": "trusted_browser", "value": "xyz"}
        ]"""
        result = parse_cookie_json(cookie_json)
        self.assertEqual(result["PHPSESSID"], "abc123")
        self.assertEqual(result["trusted_browser"], "xyz")

    def test_parse_cookie_json_object(self):
        """Test parsing JSON object format"""
        cookie_json = '{"PHPSESSID": "abc123", "trusted_browser": "xyz"}'
        result = parse_cookie_json(cookie_json)
        self.assertEqual(result["PHPSESSID"], "abc123")
        self.assertEqual(result["trusted_browser"], "xyz")

    def test_parse_cookie_json_already_parsed_list(self):
        """Test parsing already-parsed list"""
        cookie_list = [
            {"name": "PHPSESSID", "value": "abc123"},
            {"name": "trusted_browser", "value": "xyz"},
        ]
        result = parse_cookie_json(cookie_list)
        self.assertEqual(result["PHPSESSID"], "abc123")
        self.assertEqual(result["trusted_browser"], "xyz")

    def test_parse_cookie_json_invalid_raises(self):
        """Test that invalid JSON raises exception"""
        with self.assertRaises(CookieParseException):
            parse_cookie_json("not valid json")


class TestCookieFormatDetection(unittest.TestCase):
    """Test automatic cookie format detection"""

    def test_detect_format_header(self):
        """Test format detection for header string"""
        self.assertEqual(detect_cookie_format("PHPSESSID=abc"), "header")

    def test_detect_format_dict(self):
        """Test format detection for dictionary"""
        self.assertEqual(detect_cookie_format({"PHPSESSID": "abc"}), "dict")

    def test_detect_format_json_array(self):
        """Test format detection for JSON array"""
        self.assertEqual(detect_cookie_format('[{"name": "PHPSESSID"}]'), "json")

    def test_detect_format_json_object(self):
        """Test format detection for JSON object"""
        self.assertEqual(detect_cookie_format('{"PHPSESSID": "abc"}'), "json")

    def test_detect_format_list(self):
        """Test format detection for Python list"""
        self.assertEqual(detect_cookie_format([{"name": "PHPSESSID"}]), "json")

    def test_detect_format_none_raises(self):
        """Test that None raises exception"""
        with self.assertRaises(CookieParseException):
            detect_cookie_format(None)


class TestParseCookiesAutoDetect(unittest.TestCase):
    """Test the main parse_cookies function with auto-detection"""

    def test_parse_cookies_header_format(self):
        """Test automatic parsing of header format"""
        result = parse_cookies("PHPSESSID=abc123; trusted_browser=xyz")
        self.assertEqual(result["PHPSESSID"], "abc123")
        self.assertEqual(result["trusted_browser"], "xyz")

    def test_parse_cookies_dict_format(self):
        """Test automatic parsing of dict format"""
        result = parse_cookies({"PHPSESSID": "abc123", "trusted_browser": "xyz"})
        self.assertEqual(result["PHPSESSID"], "abc123")
        self.assertEqual(result["trusted_browser"], "xyz")

    def test_parse_cookies_json_format(self):
        """Test automatic parsing of JSON format"""
        result = parse_cookies('[{"name": "PHPSESSID", "value": "abc123"}]')
        self.assertEqual(result["PHPSESSID"], "abc123")

    def test_parse_cookies_empty_raises(self):
        """Test that empty cookies raise exception"""
        with self.assertRaises(CookieParseException):
            parse_cookies("")

        with self.assertRaises(CookieParseException):
            parse_cookies({})

        with self.assertRaises(CookieParseException):
            parse_cookies(None)


class TestCreateSession(unittest.TestCase):
    """Test session creation with cookies"""

    def test_create_session_basic(self):
        """Test creating session with basic cookies"""
        cookies = {"PHPSESSID": "abc123", "trusted_browser": "xyz"}
        session = create_session_from_cookies(cookies, "actian")

        # Verify session is created
        self.assertIsNotNone(session)
        self.assertIsNotNone(session.cookies)

    def test_create_session_sets_cookies(self):
        """Test that cookies are set on the session"""
        cookies = {"PHPSESSID": "abc123"}
        session = create_session_from_cookies(cookies, "actian")

        # Check cookies are present (they're set for multiple domains)
        cookie_dict = session.cookies.get_dict()
        # The cookies should be set for at least one domain
        self.assertTrue(len(session.cookies) > 0)

    def test_create_session_invalid_cookies_raises(self):
        """Test that invalid cookies raise exception"""
        with self.assertRaises(CookieParseException):
            create_session_from_cookies("not a dict", "actian")

    def test_create_session_empty_subdomain_raises(self):
        """Test that empty subdomain raises exception"""
        with self.assertRaises(ValueError):
            create_session_from_cookies({"PHPSESSID": "abc"}, "")


class TestPyBambooHRCookieAuth(unittest.TestCase):
    """Test PyBambooHR class with cookie authentication"""

    def test_init_with_cookies_string(self):
        """Test initialization with cookie string"""
        cookies = "PHPSESSID=abc123; trusted_browser=xyz"
        bamboo = PyBambooHR(subdomain="test", auth_method="cookies", cookies=cookies)

        self.assertEqual(bamboo.auth_method, "cookies")
        self.assertIsNone(bamboo.api_key)
        self.assertIsNotNone(bamboo.session)

    def test_init_with_cookies_dict(self):
        """Test initialization with cookie dictionary"""
        cookies = {"PHPSESSID": "abc123", "trusted_browser": "xyz"}
        bamboo = PyBambooHR(subdomain="test", auth_method="cookies", cookies=cookies)

        self.assertEqual(bamboo.auth_method, "cookies")
        self.assertIsNotNone(bamboo.session)

    def test_init_cookies_required_when_auth_method_cookies(self):
        """Test that cookies are required when auth_method='cookies'"""
        with self.assertRaises(ValueError) as context:
            PyBambooHR(subdomain="test", auth_method="cookies")

        self.assertIn("requires", str(context.exception).lower())

    def test_init_invalid_auth_method_raises(self):
        """Test that invalid auth_method raises exception"""
        with self.assertRaises(ValueError):
            PyBambooHR(subdomain="test", auth_method="invalid")

    def test_init_backward_compatible_api_key(self):
        """Test that API key authentication still works (backward compatibility)"""
        bamboo = PyBambooHR(subdomain="test", api_key="test_api_key")

        self.assertEqual(bamboo.auth_method, "api_key")
        self.assertEqual(bamboo.api_key, "test_api_key")
        self.assertIsNone(bamboo.session)

    @httpretty.activate
    def test_cookie_auth_request(self):
        """Test that cookie auth is used for requests"""
        # Mock the API response
        httpretty.register_uri(
            httpretty.GET,
            "https://api.bamboohr.com/api/gateway.php/test/v1/employees/directory",
            body='{"employees": [{"id": "123", "firstName": "John"}]}',
            status=200,
        )

        cookies = "PHPSESSID=test_session_id; trusted_browser=test_browser"
        bamboo = PyBambooHR(subdomain="test", auth_method="cookies", cookies=cookies)

        result = bamboo.get_employee_directory()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["firstName"], "John")

    @httpretty.activate
    def test_api_key_auth_still_works(self):
        """Test that API key auth still works with the new code"""
        # Mock the API response
        httpretty.register_uri(
            httpretty.GET,
            "https://api.bamboohr.com/api/gateway.php/test/v1/employees/directory",
            body='{"employees": [{"id": "123", "firstName": "Jane"}]}',
            status=200,
        )

        bamboo = PyBambooHR(subdomain="test", api_key="test_api_key")

        result = bamboo.get_employee_directory()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["firstName"], "Jane")

    def test_refresh_cookies(self):
        """Test refreshing cookies"""
        cookies = "PHPSESSID=old_session"
        bamboo = PyBambooHR(subdomain="test", auth_method="cookies", cookies=cookies)

        # Refresh with new cookies
        bamboo.refresh_cookies(cookies="PHPSESSID=new_session")

        # Should not raise, session should be updated
        self.assertIsNotNone(bamboo.session)

    def test_refresh_cookies_requires_cookie_auth(self):
        """Test that refresh_cookies only works with cookie auth"""
        bamboo = PyBambooHR(subdomain="test", api_key="test_api_key")

        with self.assertRaises(RuntimeError):
            bamboo.refresh_cookies(cookies="PHPSESSID=abc")


class TestCookieExpiration(unittest.TestCase):
    """Test cookie expiration handling"""

    @httpretty.activate
    def test_401_with_cookie_auth_raises_expiration(self):
        """Test that 401 response raises CookieExpiredException (when auto_refresh disabled)"""
        # Mock 401 response
        httpretty.register_uri(
            httpretty.GET,
            "https://api.bamboohr.com/api/gateway.php/test/v1/employees/directory",
            status=401,
        )

        cookies = "PHPSESSID=expired_session"
        bamboo = PyBambooHR(subdomain="test", auth_method="cookies", cookies=cookies)

        # Directly call _make_request with auto_refresh=False to test
        with self.assertRaises(CookieExpiredException):
            bamboo._make_request(
                "GET", bamboo.base_url + "employees/directory", auto_refresh=False
            )


if __name__ == "__main__":
    unittest.main()
