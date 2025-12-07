"""
Shared Logging Infrastructure for AM Portfolio Services
Centralized logging configuration for all microservices
"""

import logging
import json
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": getattr(record, "service", "unknown"),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class StructuredFormatter(logging.Formatter):
    """Structured text formatter for development"""
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.utcnow().isoformat()
        service = getattr(record, "service", "unknown")
        return f"[{timestamp}] [{record.levelname}] [{service}] {record.name}: {record.getMessage()}"


def initialize_logging(service_name: str, log_format: str = "json", log_level: str = "INFO") -> logging.Logger:
    """
    Initialize centralized logging for a service
    
    Args:
        service_name: Name of the service
        log_format: "json" for JSON format, "structured" for text format
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    
    logger = logging.getLogger(service_name)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set logging level
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Set formatter
    if log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = StructuredFormatter()
    
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    logger = logging.getLogger(name)
    return logger


def initialize_user_management_logging() -> logging.Logger:
    """Initialize logging for User Management service"""
    return initialize_logging(
        service_name="am-user-management",
        log_format="json",
        log_level="INFO"
    )


def initialize_auth_tokens_logging() -> logging.Logger:
    """Initialize logging for Auth Tokens service"""
    return initialize_logging(
        service_name="am-auth-tokens",
        log_format="json",
        log_level="INFO"
    )


def initialize_internal_service_logging() -> logging.Logger:
    """Initialize logging for Internal services"""
    return initialize_logging(
        service_name="am-internal-service",
        log_format="json",
        log_level="INFO"
    )


def initialize_api_gateway_logging() -> logging.Logger:
    """Initialize logging for API Gateway"""
    return initialize_logging(
        service_name="am-api-gateway",
        log_format="json",
        log_level="INFO"
    )


__all__ = [
    "initialize_logging",
    "get_logger",
    "initialize_user_management_logging",
    "initialize_auth_tokens_logging",
    "initialize_internal_service_logging",
    "initialize_api_gateway_logging",
    "JSONFormatter",
    "StructuredFormatter",
]
