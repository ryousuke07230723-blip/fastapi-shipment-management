from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse


class FastShipError(Exception):
    """Base exception for all exceptions in fastship api"""

    status = status.HTTP_400_BAD_REQUEST


class EntityNotFound(FastShipError):
    """Entity not found in database"""

    status = status.HTTP_404_NOT_FOUND


class ClientNotAuthorized(FastShipError):
    """Client is not authorized to perform the action"""

    status = status.HTTP_401_UNAUTHORIZED


class ClientNotVerified(FastShipError):
    """Client is not verified"""

    status = status.HTTP_401_UNAUTHORIZED


class NothingToUpdate(FastShipError):
    """No data provided to update"""


class BadCredentials(FastShipError):
    """User email or password is incorrect"""

    status = status.HTTP_401_UNAUTHORIZED


class InvalidToken(FastShipError):
    """Access token is invalid or expired"""

    status = status.HTTP_401_UNAUTHORIZED


class DeliveryPartnerNotAvailable(FastShipError):
    """Delivery partner/s do not service the destination"""

    status = status.HTTP_406_NOT_ACCEPTABLE


class DeliveryPartnerCapacityExceeded(FastShipError):
    """Delivery partner has reached their max handling capacity"""

    status = status.HTTP_406_NOT_ACCEPTABLE


def _get_handler(status: int, detail: str):
    def handler(request: Request, exception: Exception) -> Response:
        raise HTTPException(
            status_code=status,
            detail=detail,
        )

    return handler


def add_exception_handlers(app: FastAPI):
    exception_classes = FastShipError.__subclasses__()

    for exception_class in exception_classes:
        app.add_exception_handler(
            exception_class,
            _get_handler(
                status=exception_class.status,
                detail=exception_class.__doc__ or "エラーの詳細がありません",
            ),
        )

    @app.exception_handler(500)
    def internal_server_error_handler(request, exception):
        return JSONResponse(
            content={"detail": "エラーです"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            hearders={"X-Error": f"{exception}"},
        )
