from datetime import datetime, timezone


def get_delta_minutes(timestamp):
    now_utc = datetime.now(timezone.utc)
    timestamp_utc = timestamp.astimezone(timezone.utc)
    diff = now_utc - timestamp_utc
    return -round(diff.total_seconds() / 60)
