"""Errors the engine shows to a person. Messages start with Refused:."""


class EngineError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class SchemaError(EngineError):
    pass


class PathGuardError(EngineError):
    pass
