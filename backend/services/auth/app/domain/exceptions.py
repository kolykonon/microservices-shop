class DomainError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):
    pass


class AlreadyExistsError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


class InvalidRefreshTokenError(DomainError):
    pass
