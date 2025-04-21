class Error(Exception):
    """A generic Schemascii error encountered when rendering a drawing."""

    message_prefix: str | None = None

    def nice_message(self) -> str:
        return f"{self.message_prefix}{
            ": " if self.message_prefix else ""
        }{self!s}"


class DiagramSyntaxError(SyntaxError, Error):
    """Bad formatting in Schemascii diagram syntax."""
    message_prefix = "syntax error"


class TerminalsError(ValueError, Error):
    """Incorrect usage of terminals on this component."""
    message_prefix = "terminals error"


class BOMError(ValueError, Error):
    """Problem with BOM data for a component."""
    message_prefix = "BOM error"


class UnsupportedComponentError(NameError, Error):
    """Component type is not supported."""
    message_prefix = "unsupported component"


class NoDataError(ValueError, Error):
    """Data item is required, but not present."""
    message_prefix = "missing data item"


class DataTypeError(TypeError, Error):
    """Invalid data type in data section."""
    message_prefix = "invalid data type"
