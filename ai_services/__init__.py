"""
AI Services Module for CVD Planogram Optimization

This module provides AI-powered features for planogram optimization including:
- Real-time placement scoring
- Revenue prediction
- Product affinity analysis
- Demand forecasting
- Heat zone optimization
"""

from .base.client import AIClient
from .core.scoring import PlanogramScorer
from .core.prediction import RevenuePrediction
from .core.optimization import HeatZoneOptimizer
from .pipelines.cache import CacheManager

__version__ = "1.0.0"

__all__ = [
    "AIClient",
    "PlanogramScorer", 
    "RevenuePrediction",
    "HeatZoneOptimizer",
    "CacheManager"
]