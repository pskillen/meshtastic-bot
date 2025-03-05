import string
import urllib.parse
from datetime import datetime, timezone


def pretty_print_last_heard(last_heard_timestamp: int | datetime) -> str:
    if not isinstance(last_heard_timestamp, datetime):
        last_heard = datetime.fromtimestamp(last_heard_timestamp, timezone.utc)
    else:
        last_heard = last_heard_timestamp

    now = datetime.now(timezone.utc)
    delta = now - last_heard

    if delta.total_seconds() < 0:
        return "0s ago"

    if delta.days > 0:
        return f"{delta.days}d ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours}h ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes}m ago"
    else:
        return f"{delta.seconds}s ago"


_safe_chars = string.ascii_letters + string.digits + r" ()@\/.,-:\"'"


def safe_encode_node_name(name):
    return ''.join(c if c in _safe_chars else urllib.parse.quote(c) for c in name)
