from datetime import datetime, timezone


def pretty_print_last_heard(last_heard_timestamp: int) -> str:
    now = datetime.now(timezone.utc)
    last_heard = datetime.fromtimestamp(last_heard_timestamp, timezone.utc)
    delta = now - last_heard

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
