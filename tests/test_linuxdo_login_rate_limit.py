import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.linuxdo_login_rate_limit import (
    apply_linuxdo_login_rate_limit_backoff,
    clear_linuxdo_login_rate_limit_backoff_for_tests,
    detect_linuxdo_login_rate_limit,
    get_active_linuxdo_login_rate_limit_error,
)


def setup_function():
    clear_linuxdo_login_rate_limit_backoff_for_tests()


def teardown_function():
    clear_linuxdo_login_rate_limit_backoff_for_tests()


def test_detect_linuxdo_login_rate_limit_from_page_text():
    assert detect_linuxdo_login_rate_limit('Too Many Requests', '<html><body>Too Many Requests</body></html>')


def test_detect_linuxdo_login_rate_limit_from_429_title():
    assert detect_linuxdo_login_rate_limit('Error 429', '<html><body>Please retry later</body></html>')


def test_apply_linuxdo_login_rate_limit_backoff_returns_active_error():
    error_message = apply_linuxdo_login_rate_limit_backoff(
        'Linux.do login page returned Too Many Requests at https://linux.do/login',
        block_seconds=120,
        now_monotonic=100.0,
    )

    assert 'Too Many Requests' in error_message
    assert '2 more minute(s)' in error_message


def test_get_active_linuxdo_login_rate_limit_error_expires_after_backoff():
    apply_linuxdo_login_rate_limit_backoff(
        'Linux.do login page returned Too Many Requests at https://linux.do/login',
        block_seconds=1,
        now_monotonic=10.0,
    )

    assert get_active_linuxdo_login_rate_limit_error(now_monotonic=10.5) is not None
    assert get_active_linuxdo_login_rate_limit_error(now_monotonic=11.1) is None
