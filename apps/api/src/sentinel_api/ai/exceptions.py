class AIPlatformException(Exception):
    """Base exception for all AI platform operations."""

    pass


class ProviderException(AIPlatformException):
    """Raised when an LLM provider encounters an API or connection error."""

    pass


class AgentException(AIPlatformException):
    """Raised when agent execution, validation, or validation assertion fails."""

    pass


class RegistryException(AIPlatformException):
    """Raised when agent dynamic registration, lookup, or lifecycle management fails."""

    pass


class ToolException(AIPlatformException):
    """Raised when tool input validation or tool execution fails."""

    pass


class MemoryException(AIPlatformException):
    """Raised when loading or saving memory contexts fails."""

    pass


class PromptException(AIPlatformException):
    """Raised when resolving, templating, or versioning prompts fails."""

    pass
