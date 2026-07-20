"""Tests for the audit-trail logging setup."""

import logging

from oss_compliance.logging_config import get_logger


def test_get_logger_returns_configured_logger(tmp_path):
    logger = get_logger(name="test_oss_audit_logger", log_dir=str(tmp_path / "logs"))
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO
    assert len(logger.handlers) >= 1


def test_get_logger_writes_to_file(tmp_path):
    log_dir = tmp_path / "logs"
    logger = get_logger(name="test_oss_audit_logger_file", log_dir=str(log_dir))
    logger.info("scan started")
    for handler in logger.handlers:
        handler.flush()
    assert (log_dir / "audit.log").exists()
    assert "scan started" in (log_dir / "audit.log").read_text()


def test_get_logger_is_idempotent(tmp_path):
    log_dir = str(tmp_path / "logs")
    logger1 = get_logger(name="test_oss_audit_logger_idempotent", log_dir=log_dir)
    count = len(logger1.handlers)
    logger2 = get_logger(name="test_oss_audit_logger_idempotent", log_dir=log_dir)
    assert logger1 is logger2
    assert len(logger2.handlers) == count
