class Error(Exception):
    """A generic Schemascii error."""


class DiagramSyntaxError(SyntaxError, Error):
    """Bad formatting in Schemascii diagram syntax."""


class TerminalsError(TypeError, Error):
    """Incorrect usage of terminals on this component."""


class BOMError(ValueError, Error):
    """Problem with BOM data for a component."""


class UnsupportedComponentError(NameError, Error):
    """Component type is not supported."""


class NoDataError(NameError, Error):
    """Data item is required, but not present."""


class DataTypeError(ValueError, Error):
    """Invalid data value."""
