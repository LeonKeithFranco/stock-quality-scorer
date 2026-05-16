from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import DataSourceError, StockMissingError


def attach_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers on the FastAPI instance.

    Args:
        app: The FastAPI application to attach the handlers to.
    """

    @app.exception_handler(StockMissingError)
    async def stock_missing_error_handler(
        request: Request, exc: StockMissingError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "details": f"Stock with ticker symbol '{exc.ticker}' does not exist."
            },
        )

    @app.exception_handler(DataSourceError)
    async def data_source_error_handler(
        request: Request, exc: DataSourceError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "details": f"Source '{exc.source}' is temporarily unavailable. Please try again later."
            },
        )

    @app.exception_handler(Exception)
    async def catch_all_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "details": "An internal server error occurred. Please try again later."
            },
        )
