import pytest
from app.services.distance_service import DistanceService
from app.services.scoring_service import ScoringService
from app.services.feature_extraction import FeatureExtractionService
from app.services.explanation_service import ExplanationService
from app.services.ranking_service import RankingService
from app.models.domain_models import WorkerModel, Location
from app.core.config import settings

def test_haversine_distance():
    # NYC to LA rough coordinates
    nyc = (-74.0060, 40.7128)
    la = (-118.2437, 34.0522)
    dist = DistanceService.haversine_distance(nyc, la)
    assert dist > 3900 and dist < 4000  # ~3935 km

def test_estimate_arrival_time():
    time = DistanceService.estimate_arrival_time(15.0)
    assert time == 35  # 15km / 30km/h = 0.5h = 30mins + 5mins buffer

def test_feature_extraction():
    worker = WorkerModel(
        id="w1",
        is_active=True,
        is_verified=True,
        is_suspended=False,
        services=["s1"],
        location=Location(coordinates=[0.0, 0.0]),
        rating=4.0,
        experience_years=5,
        completion_rate=90.0,
        acceptance_rate=80.0,
        cancellation_rate=5.0,
        avg_response_time_mins=30.0,
        is_available=True
    )
    
    features = FeatureExtractionService.extract_features(worker, distance_km=10.0)
    
    # Distance: (50 - 10)/50 = 0.8
    assert features["distance_score"] == 0.8
    # Rating: (4.0 - 3.0)/(5.0-3.0) = 0.5
    assert features["rating_score"] == 0.5
    # Experience: 5 / 10 = 0.5
    assert features["experience_score"] == 0.5
    # Completion: 0.9
    assert features["completion_score"] == 0.9
    # Available: 1.0
    assert features["availability_score"] == 1.0
    # Response Time: (60-30)/60 = 0.5
    assert features["response_time_score"] == 0.5

def test_scoring_service():
    features = {
        "distance_score": 1.0,     # Weight 0.30
        "rating_score": 1.0,       # Weight 0.20
        "experience_score": 0.5,   # Weight 0.20 -> 0.10
        "completion_score": 1.0,   # Weight 0.15
        "availability_score": 1.0, # Weight 0.0
        "response_time_score": 1.0 # Weight 0.15
    }
    
    score = ScoringService.calculate_score(features)
    # Expected: 0.30 + 0.20 + 0.10 + 0.15 + 0 + 0.15 = 0.90 / 1.0 * 100 = 90.0
    assert score == 90.0

def test_explanation_service():
    features = {
        "distance_score": 0.9,
        "rating_score": 0.9,
        "experience_score": 0.6,
        "completion_score": 0.95,
        "response_time_score": 0.9
    }
    
    reasons = ExplanationService.generate_explanations(features)
    assert "Nearby" in reasons
    assert "Highly Rated" in reasons
    assert "Experienced" in reasons
    assert "Excellent Completion History" in reasons
    assert "Fast Responder" in reasons

def test_ranking_service():
    candidates = [
        {"worker_id": "1", "score": 85.0},
        {"worker_id": "2", "score": 92.0},
        {"worker_id": "3", "score": 75.0}
    ]
    
    ranked = RankingService.rank_candidates(candidates)
    assert ranked[0]["worker_id"] == "2"
    assert ranked[0]["ranking"] == 1
    assert ranked[0]["confidence"] == "94%"
    
    assert ranked[1]["worker_id"] == "1"
    assert ranked[1]["ranking"] == 2
    
    assert ranked[2]["worker_id"] == "3"
    assert ranked[2]["ranking"] == 3
