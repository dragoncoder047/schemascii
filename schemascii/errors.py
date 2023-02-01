class Error(Exception):
    "A generic Schemascii error."


class DiagramSyntaxError(SyntaxError, Error):
    "Bad formatting in Schemascii diagram syntax."


class TerminalsError(TypeError, Error):
    "Incorrect usage of terminals on this component."


class BOMError(ValueError, Error):
    "Problem with BOM data for a component."


class UnsupportedComponentError(NameError, Error):
    "Component type is not supported."
