import logging
from typing import List
from app.core.config import settings
from app.repositories.booking_repository import BookingRepository
from app.repositories.worker_repository import WorkerRepository
from app.services.candidate_filter import CandidateFilter
from app.services.feature_extraction import FeatureExtractionService
from app.services.scoring_service import ScoringService
from app.services.explanation_service import ExplanationService
from app.services.ranking_service import RankingService
from app.services.distance_service import DistanceService  # hoisted from inner loop
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, WorkerRecommendation
from app.core.exceptions import InfrastructureError

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, booking_repo: BookingRepository, worker_repo: WorkerRepository):
        self.booking_repo = booking_repo
        self.worker_repo = worker_repo

    async def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        logger.info(f"Generating recommendations for booking {request.booking_id}")
        
        # 1. Load Booking
        booking = await self.booking_repo.get_booking_by_id(request.booking_id)
        if not booking:
            raise InfrastructureError(f"Booking {request.booking_id} not found", status_code=404)
            
        # 2. Find all active candidates
        all_workers = await self.worker_repo.get_active_workers()
        logger.info(f"Fetched {len(all_workers)} active workers")
        
        # 3. Filter candidates
        eligible_workers = CandidateFilter.filter_candidates(all_workers, booking)
        logger.info(f"Found {len(eligible_workers)} eligible workers after filtering")
        
        candidates_data = []
        
        for worker, distance in eligible_workers:
            # 4. Extract features
            features = FeatureExtractionService.extract_features(worker, distance)
            
            # 5. Calculate Score
            score = ScoringService.calculate_score(features)
            
            # 6. Generate Explanations
            reasons = ExplanationService.generate_explanations(features)
            
            candidates_data.append({
                "worker_id": worker.id,
                "score": score,
                "confidence": "0%",  # placeholder; overwritten by RankingService
                "reasons": reasons,
                "distance_km": round(distance, 2),
                "estimated_arrival_mins": DistanceService.estimate_arrival_time(distance),
                "ranking": 0  # placeholder; overwritten by RankingService
            })
            
        # 7. Rank candidates
        ranked_candidates = RankingService.rank_candidates(candidates_data)
        
        # 8. Limit results
        max_results = request.max_results or settings.MAX_RECOMMENDATIONS
        top_candidates = ranked_candidates[:max_results]
        
        # Convert to Pydantic models
        recommendations = [
            WorkerRecommendation(**c) for c in top_candidates
        ]
        
        logger.info(
            f"Recommendation complete for booking {request.booking_id}: "
            f"evaluated={len(all_workers)}, eligible={len(eligible_workers)}, returned={len(recommendations)}"
        )
        
        return RecommendationResponse(
            booking_id=request.booking_id,
            recommendations=recommendations
        )
