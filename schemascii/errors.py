class Error(Exception):
    """A generic Schemascii error encountered when rendering a drawing."""


class DiagramSyntaxError(SyntaxError, Error):
    """Bad formatting in Schemascii diagram syntax."""


class TerminalsError(ValueError, Error):
    """Incorrect usage of terminals on this component."""


class BOMError(ValueError, Error):
    """Problem with BOM data for a component."""


class UnsupportedComponentError(NameError, Error):
    """Component type is not supported."""


class NoDataError(KeyError, Error):
    """Data item is required, but not present."""


class DataTypeError(TypeError, Error):
    """Invalid data type in data section."""
