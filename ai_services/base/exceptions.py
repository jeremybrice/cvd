"""
Custom exceptions for AI services
"""


class AIServiceError(Exception):
    """Base exception for AI service errors"""
    pass


class RateLimitError(AIServiceError):
    """Exception raised when API rate limit is exceeded"""
    pass


class TokenLimitError(AIServiceError):
    """Exception raised when token limit is exceeded"""
    pass


class CacheError(AIServiceError):
    """Exception raised for cache-related errors"""
    pass


class ValidationError(AIServiceError):
    """Exception raised for validation errors"""
    pass