from fastapi import APIRouter

from app.domain.schemas import PredictionRequest, PredictionResponse
from app.domain.service import ServiceDependency

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/", response_model=PredictionResponse)
async def predict(
    pred_req: PredictionRequest, service: ServiceDependency
) -> PredictionResponse:
    return await service.predict_outperformance(pred_req.ticker)
