from typing import List, Dict, Optional
from app.schemas.mlops import FeatureDefinition, FeatureGroup

class FeatureStoreService:
    """
    Architecture stub for Feature Store management.
    Provides interfaces for registering and validating features before training/inference.
    No online Redis/Cassandra store required for this phase.
    """
    
    def __init__(self):
        # In-memory mock for architecture purposes
        self._feature_registry: Dict[str, FeatureDefinition] = {}
        self._feature_groups: Dict[str, FeatureGroup] = {}

    def register_feature(self, feature: FeatureDefinition) -> bool:
        """Register a reusable ML feature"""
        self._feature_registry[feature.feature_name] = feature
        return True

    def register_feature_group(self, group: FeatureGroup) -> bool:
        """Group related features (e.g., worker_features, booking_features)"""
        self._feature_groups[group.group_name] = group
        for f in group.features:
            self.register_feature(f)
        return True

    def get_feature(self, feature_name: str) -> Optional[FeatureDefinition]:
        return self._feature_registry.get(feature_name)

    def get_feature_group(self, group_name: str) -> Optional[FeatureGroup]:
        return self._feature_groups.get(group_name)
