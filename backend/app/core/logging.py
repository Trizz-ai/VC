"""
Logging configuration
"""

import logging
import sys
from typing import Dict, Any

from app.core.config import settings


def setup_logging():
    """Setup application logging"""
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Configure specific loggers
    loggers = {
        "app": logging.INFO,
        "sqlalchemy.engine": logging.WARNING,
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.INFO,
    }
    
    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(level)
    
    # Add structured logging for production
    if settings.ENVIRONMENT == "production":
        setup_structured_logging()


def setup_structured_logging():
    """Setup structured logging for production"""
    
    class StructuredFormatter(logging.Formatter):
        """Custom formatter for structured JSON logs"""
        
        def format(self, record: logging.LogRecord) -> str:
            log_entry: Dict[str, Any] = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Add exception info if present
            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)
            
            # Add extra fields
            if hasattr(record, "extra"):
                log_entry.update(record.extra)
            
            return str(log_entry)
    
    # Apply structured formatter to all handlers
    for handler in logging.root.handlers:
        handler.setFormatter(StructuredFormatter())
