"""
Shared Infrastructure Module for AM Portfolio Services
Contains shared utilities, logging, and configurations
"""

from .logging import (
    initialize_logging,
    get_logger,
    initialize_user_management_logging,
    initialize_auth_tokens_logging,
    initialize_internal_service_logging,
    initialize_api_gateway_logging,
    JSONFormatter,
    StructuredFormatter,
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
