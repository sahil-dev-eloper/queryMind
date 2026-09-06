import logging
import sys


class ContextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z")
        request_id = getattr(record, "request_id", "-")
        return f"{timestamp} level={record.levelname} module={record.name} request_id={request_id} message={record.getMessage()}"


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ContextFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
