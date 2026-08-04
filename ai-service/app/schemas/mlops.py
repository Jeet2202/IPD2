from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# ==========================================
# Enums (as strings)
# ==========================================
MODEL_STATUS_ACTIVE = "ACTIVE"
MODEL_STATUS_INACTIVE = "INACTIVE"
MODEL_STATUS_DEPRECATED = "DEPRECATED"

# ==========================================
# Models & Versioning
# ==========================================
class ModelMetadata(BaseModel):
    id: str = Field(..., description="Unique identifier for the model (e.g., semantic-search-v1)")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Description of the model's purpose")
    version: str = Field(..., description="Semantic version string (e.g., 1.0.0)")
    status: str = Field(default=MODEL_STATUS_INACTIVE)
    supported_tasks: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    owner: str = Field(..., description="Team or person responsible for the model")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deployed_at: Optional[datetime] = None

class ModelRegistrationRequest(BaseModel):
    name: str
    description: str
    version: str
    supported_tasks: List[str] = []
    tags: List[str] = []
    owner: str
    notes: Optional[str] = None

class ModelVersion(BaseModel):
    version: str
    status: str
    deployed_at: Optional[datetime] = None

# ==========================================
# Datasets
# ==========================================
class DatasetMetadata(BaseModel):
    id: str
    name: str
    version: str
    description: str
    source: str = Field(..., description="S3 bucket, DB collection, or file path")
    schema_definition: Dict[str, str] = Field(default_factory=dict, description="Column/Field mapping to types")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Row count, size, etc.")
    feature_list: List[str] = Field(default_factory=list)
    supported_models: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DatasetRegistrationRequest(BaseModel):
    name: str
    version: str
    description: str
    source: str
    schema_definition: Dict[str, str] = {}
    statistics: Dict[str, Any] = {}
    feature_list: List[str] = []
    supported_models: List[str] = []

# ==========================================
# Feature Store Architecture
# ==========================================
class FeatureDefinition(BaseModel):
    feature_name: str
    dtype: str
    description: str
    validation_rules: Dict[str, Any] = {}

class FeatureGroup(BaseModel):
    group_name: str
    description: str
    features: List[FeatureDefinition] = []

# ==========================================
# Experiment Tracking
# ==========================================
class ExperimentMetadata(BaseModel):
    id: str
    name: str
    model_id: str
    dataset_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="COMPLETED") # RUNNING, FAILED, COMPLETED
    execution_time_seconds: float = 0.0
    owner: str
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExperimentRequest(BaseModel):
    name: str
    model_id: str
    dataset_id: str
    parameters: Dict[str, Any] = {}
    metrics: Dict[str, float] = {}
    results: Dict[str, Any] = {}
    status: str = "COMPLETED"
    execution_time_seconds: float = 0.0
    owner: str
    notes: Optional[str] = None

# ==========================================
# Monitoring & Health
# ==========================================
class ModelMetrics(BaseModel):
    model_id: str
    inference_count: int = 0
    inference_latency_ms: float = 0.0
    error_rate: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AIHealthStatus(BaseModel):
    status: str = "HEALTHY"
    overall_score: float = 100.0
    database_status: str = "CONNECTED"
    embedding_status: str = "ONLINE"
    model_status: str = "ONLINE"
    dataset_status: str = "ONLINE"
    api_status: str = "ONLINE"
    groq_connectivity: str = "ONLINE"
    cache_status: str = "ONLINE"
    filesystem_status: str = "ONLINE"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ==========================================
# Audit & Configuration
# ==========================================
class AuditLogEntry(BaseModel):
    id: Optional[str] = None
    event_type: str = Field(..., description="MODEL_LOADED, CONFIG_CHANGED, INFERENCE_FAILURE, etc.")
    entity_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    level: str = Field(default="INFO") # INFO, WARNING, ERROR
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SystemConfiguration(BaseModel):
    id: str = Field(default="global")
    model_paths: Dict[str, str] = Field(default_factory=dict)
    dataset_paths: Dict[str, str] = Field(default_factory=dict)
    thresholds: Dict[str, float] = Field(default_factory=dict)
    feature_flags: Dict[str, bool] = Field(default_factory=dict)
    rate_limits: Dict[str, int] = Field(default_factory=dict)
    timeouts_seconds: Dict[str, float] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
