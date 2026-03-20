from app.core.messages import APP_ERROR, AUTHENTICATION_REQUIRED, AUTHORIZATION_REQUIRED, NOT_FOUND, VALIDATION_FAILED


class AppError(Exception):
    status_code = 400
    detail = APP_ERROR

    def __init__(self, detail: str | None = None):
        super().__init__(detail or self.detail)
        self.detail = detail or self.detail


class AuthenticationError(AppError):
    status_code = 401
    detail = AUTHENTICATION_REQUIRED


class AuthorizationError(AppError):
    status_code = 403
    detail = AUTHORIZATION_REQUIRED


class NotFoundError(AppError):
    status_code = 404
    detail = NOT_FOUND


class ValidationAppError(AppError):
    status_code = 422
    detail = VALIDATION_FAILED
