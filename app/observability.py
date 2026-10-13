"""Structured events intentionally exclude user text and exception messages."""
import json
import logging

logger = logging.getLogger("ai_serving")


def configure_logging(level: str) -> None:
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
    logger.setLevel(level)
    logger.propagate = False


def event(name: str, level: int = logging.INFO, **fields: object) -> None:
    logger.log(level, json.dumps({"event": name, **fields}, separators=(",", ":")))
