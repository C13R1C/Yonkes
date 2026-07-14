import hashlib

from django.conf import settings
from django.core.cache import cache

def _attempts():
    return getattr(settings, "LOGIN_RATE_LIMIT_ATTEMPTS", 5)


def _window():
    return getattr(settings, "LOGIN_RATE_LIMIT_WINDOW", 300)


def _client_ip(request):
    return request.META.get("REMOTE_ADDR", "") or "unknown"


def _key(username, ip):
    material = f"{ip}:{(username or '').strip().lower()}".encode()
    return "login-rate:" + hashlib.sha256(material).hexdigest()


def is_login_blocked(request, username):
    return int(cache.get(_key(username, _client_ip(request)), 0)) >= _attempts()


def record_login_failure(request, username):
    key = _key(username, _client_ip(request))
    count = int(cache.get(key, 0)) + 1
    cache.set(key, count, _window())
    return count


def clear_login_failures(request, username):
    cache.delete(_key(username, _client_ip(request)))
