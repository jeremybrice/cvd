"""
Real-time planogram scoring service

Provides instant feedback on planogram placement quality
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base.client import AIClient
from ..base.exceptions import AIServiceError, ValidationError
from ..pipelines.cache import CacheManager, cached

logger = logging.getLogger(__name__)


class PlanogramScorer:
    """
    Real-time scoring for planogram placements
    
    Evaluates placement quality based on:
    - Product visibility zones
    - Adjacent product affinity
    - Category coherence
    - Revenue potential
    """
    
    # Zone score weights
    ZONE_WEIGHTS = {
        "eye_level": 1.0,      # 52-65 inches
        "reach_level": 0.85,   # 38-52 inches  
        "stoop_level": 0.65,   # 24-38 inches
        "floor_level": 0.5     # 0-24 inches
    }
    
    def __init__(
        self,
        ai_client: Optional[AIClient] = None,
        cache_manager: Optional[CacheManager] = None
    ):
        """
        Initialize the scorer
        
        Args:
            ai_client: AI client instance
            cache_manager: Cache manager instance
        """
        self.ai_client = ai_client or AIClient()
        self.cache_manager = cache_manager or CacheManager()
    
    @cached(cache_manager=None, ttl=300)  # 5 minute cache
    def score_placement(
        self,
        planogram_data: Dict[str, Any],
        product_id: int,
        slot_position: Dict[str, int],
        historical_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Score a single product placement
        
        Args:
            planogram_data: Complete planogram configuration
            product_id: Product being placed
            slot_position: Position (row, column, cabinet)
            historical_data: Optional historical sales data
        
        Returns:
            Score dictionary with details
        """
        try:
            # Validate inputs
            self._validate_inputs(planogram_data, product_id, slot_position)
            
            # Calculate component scores
            zone_score = self._calculate_zone_score(slot_position)
            affinity_score = self._calculate_affinity_score(
                planogram_data, product_id, slot_position
            )
            category_score = self._calculate_category_score(
                planogram_data, product_id, slot_position
            )
            
            # Get AI-enhanced score if available
            ai_score = self._get_ai_score(
                planogram_data, product_id, slot_position, historical_data
            )
            
            # Combine scores (weighted average)
            final_score = self._combine_scores({
                "zone": zone_score * 0.3,
                "affinity": affinity_score * 0.25,
                "category": category_score * 0.2,
                "ai": ai_score * 0.25 if ai_score else 0
            })
            
            # Generate feedback
            feedback = self._generate_feedback(
                final_score, zone_score, affinity_score, category_score
            )
            
            return {
                "score": round(final_score, 1),
                "components": {
                    "zone_score": zone_score,
                    "affinity_score": affinity_score,
                    "category_score": category_score,
                    "ai_score": ai_score
                },
                "feedback": feedback,
                "suggestions": self._generate_suggestions(
                    final_score, planogram_data, product_id
                ),
                "confidence": self._calculate_confidence(ai_score is not None),
                "timestamp": datetime.now().isoformat()
            }
            
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Scoring error: {e}")
            return self._fallback_score()
    
    def _validate_inputs(
        self,
        planogram_data: Dict,
        product_id: int,
        slot_position: Dict
    ):
        """Validate input parameters"""
        if not planogram_data:
            raise ValidationError("Planogram data is required")
        
        if not isinstance(product_id, int) or product_id <= 0:
            raise ValidationError("Valid product ID is required")
        
        required_keys = ["row", "column"]
        for key in required_keys:
            if key not in slot_position:
                raise ValidationError(f"Slot position must include {key}")
    
    def _calculate_zone_score(self, slot_position: Dict) -> float:
        """
        Calculate score based on visibility zone
        
        Args:
            slot_position: Position with row information
        
        Returns:
            Zone score (0-100)
        """
        row = slot_position.get("row", 0)
        
        # Map row to zone (assuming 6 rows)
        if row <= 1:  # Top rows (eye level)
            zone = "eye_level"
        elif row <= 3:  # Middle rows (reach level)
            zone = "reach_level"
        elif row <= 4:  # Lower rows (stoop level)
            zone = "stoop_level"
        else:  # Bottom rows
            zone = "floor_level"
        
        return self.ZONE_WEIGHTS.get(zone, 0.5) * 100
    
    def _calculate_affinity_score(
        self,
        planogram_data: Dict,
        product_id: int,
        slot_position: Dict
    ) -> float:
        """
        Calculate score based on adjacent product affinity
        
        Args:
            planogram_data: Complete planogram
            product_id: Product being placed
            slot_position: Position
        
        Returns:
            Affinity score (0-100)
        """
        # Find adjacent products
        adjacent_products = self._get_adjacent_products(
            planogram_data, slot_position
        )
        
        if not adjacent_products:
            return 50  # Neutral score if no adjacent products
        
        # Simple affinity calculation (can be enhanced with real data)
        # For now, products in same category score higher
        affinity_sum = 0
        for adj_product in adjacent_products:
            if self._same_category(product_id, adj_product):
                affinity_sum += 80
            else:
                affinity_sum += 40
        
        return min(affinity_sum / len(adjacent_products), 100)
    
    def _calculate_category_score(
        self,
        planogram_data: Dict,
        product_id: int,
        slot_position: Dict
    ) -> float:
        """
        Calculate score based on category coherence
        
        Returns:
            Category score (0-100)
        """
        # Check if product category matches zone expectations
        # For example, beverages typically go in coolers
        # Snacks at eye level, etc.
        
        # Simplified logic
        row = slot_position.get("row", 0)
        
        # Assume beverages should be in lower rows (cooler)
        if product_id <= 4:  # Beverage IDs
            if row >= 3:
                return 90
            else:
                return 60
        
        # Snacks should be at eye/reach level
        elif product_id <= 8:  # Snack IDs
            if row <= 3:
                return 90
            else:
                return 60
        
        # Other products
        return 75
    
    def _get_ai_score(
        self,
        planogram_data: Dict,
        product_id: int,
        slot_position: Dict,
        historical_data: Optional[Dict]
    ) -> Optional[float]:
        """
        Get AI-enhanced score from Claude
        
        Returns:
            AI score or None if unavailable
        """
        if self.ai_client.fallback_mode:
            return None
        
        try:
            # Prepare context for AI
            prompt = self._build_ai_prompt(
                planogram_data, product_id, slot_position, historical_data
            )
            
            # Get AI response
            response = self.ai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are an expert in retail merchandising and planogram optimization. Analyze the product placement and provide a score from 0-100.",
                max_tokens=200,
                temperature=0.3
            )
            
            # Parse response
            content = response.get("content", "{}")
            try:
                result = json.loads(content)
                return float(result.get("score", 75))
            except (json.JSONDecodeError, ValueError):
                logger.warning("Failed to parse AI response")
                return None
                
        except Exception as e:
            logger.error(f"AI scoring error: {e}")
            return None
    
    def _build_ai_prompt(
        self,
        planogram_data: Dict,
        product_id: int,
        slot_position: Dict,
        historical_data: Optional[Dict]
    ) -> str:
        """Build prompt for AI scoring"""
        prompt = f"""
        Analyze this product placement and provide a score (0-100):
        
        Product ID: {product_id}
        Position: Row {slot_position.get('row')}, Column {slot_position.get('column')}
        Cabinet: {slot_position.get('cabinet', 'main')}
        
        Context:
        - Total slots: {len(planogram_data.get('slots', []))}
        - Adjacent products: {self._get_adjacent_products(planogram_data, slot_position)}
        
        Provide response as JSON: {{"score": <number>, "reason": "<brief explanation>"}}
        """
        
        if historical_data:
            prompt += f"\nHistorical performance: {json.dumps(historical_data)}"
        
        return prompt
    
    def _get_adjacent_products(
        self,
        planogram_data: Dict,
        slot_position: Dict
    ) -> List[int]:
        """Get list of adjacent product IDs"""
        adjacent = []
        row = slot_position.get("row")
        col = slot_position.get("column")
        
        # Check surrounding positions
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                
                # Find product at adjacent position
                for slot in planogram_data.get("slots", []):
                    if (slot.get("row") == row + dr and 
                        slot.get("column") == col + dc):
                        product = slot.get("product_id")
                        if product:
                            adjacent.append(product)
        
        return adjacent
    
    def _same_category(self, product1: int, product2: int) -> bool:
        """Check if two products are in the same category"""
        # Simplified category mapping
        categories = {
            "beverages": [1, 2, 3, 4],
            "snacks": [5, 6, 7, 8],
            "candy": [9, 10, 11, 12]
        }
        
        for category, products in categories.items():
            if product1 in products and product2 in products:
                return True
        
        return False
    
    def _combine_scores(self, scores: Dict[str, float]) -> float:
        """Combine component scores into final score"""
        total = sum(scores.values())
        count = sum(1 for v in scores.values() if v > 0)
        
        if count == 0:
            return 50  # Default neutral score
        
        # Adjust for missing AI score
        if scores.get("ai", 0) == 0:
            # Redistribute AI weight to other components
            total = total * 1.33
        
        return min(total, 100)
    
    def _generate_feedback(
        self,
        final_score: float,
        zone_score: float,
        affinity_score: float,
        category_score: float
    ) -> str:
        """Generate human-readable feedback"""
        if final_score >= 80:
            level = "Excellent"
        elif final_score >= 60:
            level = "Good"
        elif final_score >= 40:
            level = "Fair"
        else:
            level = "Poor"
        
        feedback = f"{level} placement (Score: {final_score:.0f}/100). "
        
        # Add specific feedback
        if zone_score < 60:
            feedback += "Consider moving to a higher visibility zone. "
        if affinity_score < 60:
            feedback += "Adjacent products have low affinity. "
        if category_score < 60:
            feedback += "Product category doesn't match zone expectations. "
        
        return feedback.strip()
    
    def _generate_suggestions(
        self,
        score: float,
        planogram_data: Dict,
        product_id: int
    ) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if score < 80:
            suggestions.append("Move product to eye-level for better visibility")
        
        if score < 60:
            suggestions.append("Place near complementary products")
            suggestions.append("Consider category zoning guidelines")
        
        if score < 40:
            suggestions.append("This placement may significantly impact sales")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _calculate_confidence(self, has_ai: bool) -> str:
        """Calculate confidence level"""
        if has_ai:
            return "high"
        else:
            return "medium"
    
    def _fallback_score(self) -> Dict[str, Any]:
        """Fallback scoring when service fails"""
        return {
            "score": 75,
            "components": {
                "zone_score": 75,
                "affinity_score": 75,
                "category_score": 75,
                "ai_score": None
            },
            "feedback": "Scoring service temporarily unavailable. Using baseline score.",
            "suggestions": [],
            "confidence": "low",
            "timestamp": datetime.now().isoformat()
        }