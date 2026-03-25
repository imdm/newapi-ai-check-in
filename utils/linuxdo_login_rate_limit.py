#!/usr/bin/env python3
"""
Linux.do 登录限流检测与本轮运行短路状态。
"""

import math
import time

_DEFAULT_LINUXDO_LOGIN_RATE_LIMIT_BACKOFF_SECONDS = 1800
_linuxdo_login_rate_limited_until_monotonic = 0.0
_linuxdo_login_rate_limit_reason = ''


def detect_linuxdo_login_rate_limit(page_title: str, page_content: str) -> bool:
    """检测 Linux.do 页面是否返回了 Too Many Requests 限流页。"""
    normalized_title = (page_title or '').lower()
    normalized_content = (page_content or '').lower()

    if 'too many requests' in normalized_title or 'too many requests' in normalized_content:
        return True

    return 'error 429' in normalized_title or 'error 429' in normalized_content


def get_active_linuxdo_login_rate_limit_error(now_monotonic: float | None = None) -> str | None:
    """返回当前仍生效的 Linux.do 登录限流错误信息。"""
    current_monotonic = now_monotonic if now_monotonic is not None else time.monotonic()
    remaining_seconds = _linuxdo_login_rate_limited_until_monotonic - current_monotonic
    if remaining_seconds <= 0:
        return None

    remaining_minutes = max(1, math.ceil(remaining_seconds / 60))
    reason_suffix = f' Reason: {_linuxdo_login_rate_limit_reason}' if _linuxdo_login_rate_limit_reason else ''
    return (
        'Linux.do login is temporarily rate limited (Too Many Requests); '
        f'skipping new Linux.do login attempts for this run for about {remaining_minutes} more minute(s).'
        f'{reason_suffix}'
    )


def apply_linuxdo_login_rate_limit_backoff(
    reason: str,
    block_seconds: int = _DEFAULT_LINUXDO_LOGIN_RATE_LIMIT_BACKOFF_SECONDS,
    now_monotonic: float | None = None,
) -> str:
    """记录 Linux.do 登录限流状态，并返回当前错误信息。"""
    global _linuxdo_login_rate_limited_until_monotonic
    global _linuxdo_login_rate_limit_reason

    current_monotonic = now_monotonic if now_monotonic is not None else time.monotonic()
    _linuxdo_login_rate_limited_until_monotonic = current_monotonic + block_seconds
    _linuxdo_login_rate_limit_reason = reason
    return get_active_linuxdo_login_rate_limit_error(current_monotonic) or (
        'Linux.do login is temporarily rate limited (Too Many Requests).'
    )


def clear_linuxdo_login_rate_limit_backoff_for_tests() -> None:
    """清理 Linux.do 登录限流状态，仅供测试使用。"""
    global _linuxdo_login_rate_limited_until_monotonic
    global _linuxdo_login_rate_limit_reason

    _linuxdo_login_rate_limited_until_monotonic = 0.0
    _linuxdo_login_rate_limit_reason = ''
