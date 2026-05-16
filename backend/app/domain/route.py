from fastapi import APIRouter

from app.domain.schemas import PredictionRequest, PredictionResponse
from app.domain.service import ServiceDependency

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/", response_model=PredictionResponse)
async def predict(
    pred_req: PredictionRequest, service: ServiceDependency
) -> PredictionResponse:
    """Return an outperformance prediction for a single stock ticker.

    Args:
        pred_req: The request body containing the ticker symbol.
        service: The injected Service instance.

    Returns:
        PredictionResponse: The outperformance prediction for the ticker.
    """
    return await service.predict_outperformance(pred_req.ticker)


@router.post("/snp-500", response_model=list[PredictionResponse])
async def predict_snp_500(service: ServiceDependency) -> list[PredictionResponse]:
    """Return outperformance predictions for all current S&P 500 constituents.

    Args:
        service: The injected Service instance.

    Returns:
        list[PredictionResponse]: Predictions for each S&P 500 ticker that completed
            successfully.
    """
    return await service.predict_outperformance_of_snp_500()
