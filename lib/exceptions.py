"""Define custom exceptions."""

class FollowerException(Exception):

    """Base exception for follower-related exceptions."""

    def __str__(self):
        """Define a human-readable name for exception.

        Note that this name should be equal to the name used
        in strategy YAML files when describing the expected 
        result of a follow action.

        :returns: Name of exception.

        """
        return "FollowerException"

class IntersectionException(FollowerException):

    """Raised when follower detects an intersection."""

    def __str__(self):
        """Define a human-readable name for exception.

        Note that this name should be equal to the name used
        in strategy YAML files when describing the expected 
        result of a follow action.

        :returns: Name of exception.

        """
        return "IntersectionException"

class BoxException(FollowerException):

    """Raised when follower detects a blue firing box."""

    def __str__(self):
        """Define a human-readable name for exception.

        Note that this name should be equal to the name used
        in strategy YAML files when describing the expected 
        result of a follow action.

        :returns: Name of exception.

        """
        return "BoxException"
