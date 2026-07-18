class AppException(Exception):
    """Base application exception.

    All custom API exceptions should inherit from this.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


class DatabaseException(AppException):
    """Raised when a database operation or query fails."""

    def __init__(
        self, message: str, error_code: str = "DATABASE_ERROR", status_code: int = 500
    ):
        super().__init__(message, error_code, status_code)


class EntityNotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(
        self, message: str, error_code: str = "NOT_FOUND", status_code: int = 404
    ):
        super().__init__(message, error_code, status_code)


class ConfigurationException(AppException):
    """Raised when configuration variables are missing or invalid."""

    def __init__(
        self,
        message: str,
        error_code: str = "CONFIGURATION_ERROR",
        status_code: int = 500,
    ):
        super().__init__(message, error_code, status_code)


class ValidationException(AppException):
    """Raised when a business rule or inputs fail validation."""

    def __init__(
        self, message: str, error_code: str = "VALIDATION_ERROR", status_code: int = 400
    ):
        super().__init__(message, error_code, status_code)
