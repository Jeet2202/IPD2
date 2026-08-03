from fastapi import APIRouter, Depends
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import RecommendationService
from app.repositories.booking_repository import BookingRepository
from app.repositories.worker_repository import WorkerRepository
from app.core.dependencies import get_db

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

def get_recommendation_service(db=Depends(get_db)) -> RecommendationService:
    booking_repo = BookingRepository(db)
    worker_repo = WorkerRepository(db)
    return RecommendationService(booking_repo, worker_repo)

@router.post("/workers", response_model=RecommendationResponse)
async def recommend_workers(
    request: RecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Intelligently recommend the most suitable workers for a booking request.
    """
    return await service.get_recommendations(request)
