# logger.py (fix: keine %f im datefmt, msecs über %(msecs)03d)
import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime

try:
    import colorama  # optional
    colorama.just_fix_windows_console()
except Exception:
    pass

_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

LEVEL_COLORS = {
    "DEBUG": "\033[36m",
    "INFO": "\033[32m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[35m",
}
RESET = "\033[0m"

TIME_FMT = "%Y-%m-%d %H:%M:%S"  # kein %f!
BASE_FMT = "%(asctime)s.%(msecs)03d | %(levelname)s | %(name)s:%(lineno)d | %(message)s"


class ColorFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt=BASE_FMT, datefmt=TIME_FMT)

    def format(self, record: logging.LogRecord) -> str:
        # Färbe nur das Level, wenn ein TTY vorhanden ist
        if sys.stderr.isatty():
            levelname = record.levelname
            color = LEVEL_COLORS.get(levelname, "")
            original = record.levelname
            record.levelname = f"{color}{original}{RESET}"
            try:
                return super().format(record)
            finally:
                record.levelname = original
        return super().format(record)


class JsonFormatter(logging.Formatter):
    # JSON ist unabhängig vom strftime-Format (nutzt datetime direkt)
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "line": record.lineno,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _level_from_str(level_str: str) -> int:
    return getattr(logging, level_str.upper(), logging.INFO)


def get_logger(
    name: str | None = None,
    *,
    level: str | int = _LEVEL,
    to_console: bool = True,
    log_file: str | None = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    json_console: bool = False,
    json_file: bool = False,
) -> logging.Logger:
    """
    Erzeugt einen Logger mit optionaler Console- und Rotating-File-Ausgabe.
    """
    logger = logging.getLogger(name if name else "")
    if logger.handlers:
        return logger

    logger.setLevel(_level_from_str(level) if isinstance(level, str) else level)
    logger.propagate = False

    if to_console:
        ch = logging.StreamHandler(stream=sys.stderr)
        ch.setLevel(logger.level)
        ch.setFormatter(JsonFormatter() if json_console else ColorFormatter())
        logger.addHandler(ch)

    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        fh = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        fh.setLevel(logger.level)
        if json_file:
            fh.setFormatter(JsonFormatter())
        else:
            fh.setFormatter(logging.Formatter(fmt=BASE_FMT, datefmt=TIME_FMT))
        logger.addHandler(fh)

    return logger


if __name__ == "__main__":
    log = get_logger("demo", log_file="logs/app.log")
    log.debug("Debug an")
    log.info("Hallo Logger 👋")
    log.warning("Achtung, etwas ist ungewöhnlich.")
    try:
        1 / 0
    except ZeroDivisionError:
        log.exception("Fehler passiert")
