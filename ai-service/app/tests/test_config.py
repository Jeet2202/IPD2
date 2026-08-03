from app.core.config import Settings

def test_settings_default_values():
    settings = Settings()
    assert settings.ENVIRONMENT == "development"
    assert settings.LOGGING_LEVEL == "INFO"
    assert settings.MONGO_URI.startswith("mongodb")  # accepts mongodb:// and mongodb+srv://
    assert settings.MAX_QUERY_LENGTH == 500

def test_cors_origins_parsing():
    settings = Settings(CORS_ORIGINS="http://localhost:3000,http://localhost:8080")
    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) == 2
    assert "http://localhost:3000" in settings.CORS_ORIGINS

def test_cors_origins_list():
    settings = Settings(CORS_ORIGINS=["http://localhost:3000"])
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.CORS_ORIGINS[0] == "http://localhost:3000"

def test_recommendation_weights_sum():
    """Verify default recommendation weights sum to 1.0 (excluding availability=0.0)"""
    s = Settings()
    total = (
        s.WEIGHT_DISTANCE + s.WEIGHT_RATING + s.WEIGHT_EXPERIENCE +
        s.WEIGHT_COMPLETION + s.WEIGHT_AVAILABILITY + s.WEIGHT_RESPONSE_TIME
    )
    assert abs(total - 1.0) < 1e-9, f"Weights should sum to 1.0, got {total}"

def test_search_weights_sum():
    """Verify default search weights sum to 1.0"""
    s = Settings()
    total = s.WEIGHT_SEMANTIC + s.WEIGHT_KEYWORD + s.WEIGHT_POPULARITY
    assert abs(total - 1.0) < 1e-9, f"Search weights should sum to 1.0, got {total}"
