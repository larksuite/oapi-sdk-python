class RegisterAppError(Exception):
    def __init__(self, code: str, description: str):
        self.code = code
        self.description = description
        super().__init__(f"{code}: {description}")


class AppAccessDeniedError(RegisterAppError):
    ...


class AppExpiredError(RegisterAppError):
    ...
