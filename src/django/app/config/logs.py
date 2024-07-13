import json_log_formatter

from datetime import datetime
from datetime import timezone


class JSONFormatter(json_log_formatter.JSONFormatter):

    def json_record(self, message, extra, record):
        dt = datetime.fromtimestamp(record.created, timezone.utc)

        extra.update(
            {
                "time": dt.isoformat(),
                "level": record.levelname,
                "source": "django",
                "pathname": record.pathname,
                "lineno": record.lineno,
            }
        )

        return super().json_record(message, extra, record)
