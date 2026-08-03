import pytest
from app.services.historical_analysis_service import HistoricalAnalysisService
from app.services.demand_analysis_service import DemandAnalysisService
from app.services.pricing_confidence_service import PricingConfidenceService
from app.services.outlier_detection_service import OutlierDetectionService
from app.services.pricing_feature_generator import PricingFeatureGenerator
from app.schemas.pricing import HistoricalSummary, PricingEstimateRequest
from app.models.domain_models import QuotationModel
from app.core.config import settings

def test_historical_analysis():
    quotations = [
        QuotationModel(id="1", booking_id="b1", worker_id="w1", amount=500.0, status="accepted", created_at=""),
        QuotationModel(id="2", booking_id="b2", worker_id="w2", amount=600.0, status="accepted", created_at=""),
        QuotationModel(id="3", booking_id="b3", worker_id="w3", amount=550.0, status="accepted", created_at=""),
    ]
    
    summary = HistoricalAnalysisService.analyze_history(quotations)
    
    assert summary.data_points == 3
    assert summary.min_price == 500.0
    assert summary.max_price == 600.0
    assert summary.avg_price == 550.0
    assert summary.median_price == 550.0

def test_historical_analysis_empty():
    summary = HistoricalAnalysisService.analyze_history([])
    assert summary.data_points == 0
    assert summary.avg_price == 0.0

def test_demand_analysis():
    # 80% busy -> Peak
    assert DemandAnalysisService.calculate_demand_level({"total": 10, "available": 2}) == "Peak"
    
    # 70% busy -> High
    assert DemandAnalysisService.calculate_demand_level({"total": 10, "available": 3}) == "High"
    
    # 10% busy -> Low
    assert DemandAnalysisService.calculate_demand_level({"total": 10, "available": 9}) == "Low"
    
    # 50% busy -> Normal
    assert DemandAnalysisService.calculate_demand_level({"total": 10, "available": 5}) == "Normal"
    
    # No data -> Normal
    assert DemandAnalysisService.calculate_demand_level({}) == "Normal"

def test_pricing_confidence():
    # Good data volume, stable variance
    summary1 = HistoricalSummary(min_price=100, max_price=110, avg_price=105, median_price=105, std_dev=3, data_points=25)
    conf1 = PricingConfidenceService.calculate_confidence(summary1, "Normal")
    assert conf1 == 100 # 50 + 30 (vol) + 20 (var)
    
    # Low data, high variance
    summary2 = HistoricalSummary(min_price=100, max_price=300, avg_price=200, median_price=200, std_dev=120, data_points=6)
    conf2 = PricingConfidenceService.calculate_confidence(summary2, "Normal")
    assert conf2 == 40 # 50 + 10 (vol) - 20 (var)
    
    # Peak demand penalty
    conf3 = PricingConfidenceService.calculate_confidence(summary1, "Peak")
    assert conf3 == 90 # 100 - 10

def test_outlier_detection_clamp():
    # Clamp to max allowed variance (50% default)
    base = 1000.0
    clamped_high = OutlierDetectionService.clamp_price(2000.0, base)
    assert clamped_high == 1500.0
    
    clamped_low = OutlierDetectionService.clamp_price(100.0, base)
    assert clamped_low == 500.0
    
    clamped_normal = OutlierDetectionService.clamp_price(1100.0, base)
    assert clamped_normal == 1100.0

def test_feature_generator():
    req = PricingEstimateRequest(
        booking_id="1",
        city="Mumbai",
        urgency_level="critical",
        preferred_date="2026-08-08", # Saturday
        complexity_level="high"
    )
    
    features = PricingFeatureGenerator.extract_features(req)
    assert features["is_weekend"] is True
    assert features["is_urgent"] is True
    assert features["is_complex"] is True
