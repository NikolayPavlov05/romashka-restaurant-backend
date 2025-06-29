import re

from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import UserRateThrottle

_rate_limits = {}


class BaseRateLimit(UserRateThrottle):
    _DURATION_DICT = {"s": 1, "m": 60, "h": 3600, "d": 86400}

    def parse_rate(self, rate: str):
        if rate is None:
            return None, None

        requests_count, period = rate.split("/")
        if periods_count := re.findall(r"\d+", period):
            periods_count = periods_count[0]
            period = period.replace(periods_count, "")
        else:
            periods_count = 1

        duration = self._DURATION_DICT[period[0]] * int(periods_count)
        return int(requests_count), duration


class AnonRateLimit(AnonRateThrottle, BaseRateLimit): ...


def rate_limit(rate: str, scope: str = "user", bases: tuple[type] = (BaseRateLimit,)):
    _rate, _scope = rate, scope

    if rate_limit_class := _rate_limits.get((rate, scope, bases)):
        return rate_limit_class

    class _RateLimit(*bases):
        rate = _rate
        scope = _scope

    _rate_limits[(rate, scope, bases)] = _RateLimit
    return _RateLimit


def anon_rate_limit(rate: str, bases: tuple[type] = (AnonRateLimit,)):
    return rate_limit(rate, "anon", bases)
