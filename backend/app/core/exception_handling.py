from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import StockMissingError


def attach_exception_handlers(app: FastAPI) -> None:
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
