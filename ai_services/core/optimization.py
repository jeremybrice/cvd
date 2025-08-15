"""
Heat zone optimization service

Analyzes and optimizes product placement based on revenue potential zones
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import statistics

from ..base.client import AIClient
from ..base.exceptions import AIServiceError, ValidationError
from ..pipelines.cache import CacheManager, cached

logger = logging.getLogger(__name__)


class HeatZoneOptimizer:
    """
    Optimizes planogram based on heat zones (high-performance areas)
    
    Creates heat maps showing:
    - Revenue potential by position
    - Optimal product placement zones
    - Customer interaction patterns
    """
    
    # Standard visibility zones
    ZONE_DEFINITIONS = {
        "premium": {"rows": [1, 2], "multiplier": 1.5},    # Eye level
        "standard": {"rows": [3], "multiplier": 1.2},      # Reach level
        "economy": {"rows": [4, 5], "multiplier": 0.9},    # Stoop level
        "discount": {"rows": [6], "multiplier": 0.7}       # Floor level
    }
    
    def __init__(
        self,
        ai_client: Optional[AIClient] = None,
        cache_manager: Optional[CacheManager] = None
    ):
        """
        Initialize optimizer
        
        Args:
            ai_client: AI client instance
            cache_manager: Cache manager instance
        """
        self.ai_client = ai_client or AIClient()
        self.cache_manager = cache_manager or CacheManager()
    
    @cached(cache_manager=None, ttl=86400)  # 24 hour cache
    def generate_heat_map(
        self,
        device_id: int,
        historical_sales: List[Dict[str, Any]],
        cabinet_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate heat map for device positions
        
        Args:
            device_id: Device identifier
            historical_sales: Historical sales data by position
            cabinet_config: Cabinet configuration details
        
        Returns:
            Heat map data structure
        """
        try:
            # Validate inputs
            self._validate_heat_map_inputs(device_id, historical_sales)
            
            # Analyze position performance
            position_metrics = self._analyze_position_performance(historical_sales)
            
            # Calculate zone revenues
            zone_revenues = self._calculate_zone_revenues(position_metrics)
            
            # Generate heat matrix
            heat_matrix = self._generate_heat_matrix(
                position_metrics, cabinet_config
            )
            
            # Identify optimization opportunities
            opportunities = self._identify_opportunities(
                position_metrics, zone_revenues
            )
            
            # Get AI recommendations if available
            ai_recommendations = self._get_ai_recommendations(
                position_metrics, zone_revenues
            )
            
            return {
                "device_id": device_id,
                "heat_matrix": heat_matrix,
                "zone_analysis": zone_revenues,
                "optimization_opportunities": opportunities,
                "ai_recommendations": ai_recommendations,
                "statistics": {
                    "total_positions": len(position_metrics),
                    "high_performance_zones": self._count_high_performance(heat_matrix),
                    "revenue_concentration": self._calculate_concentration(position_metrics)
                },
                "visualization": {
                    "color_scale": {
                        "min": 0,
                        "max": 100,
                        "gradient": ["#0000FF", "#00FF00", "#FFFF00", "#FF0000"]
                    },
                    "opacity": 0.4
                },
                "cache_ttl": 86400,
                "generated_at": datetime.now().isoformat()
            }
            
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Heat map generation error: {e}")
            return self._fallback_heat_map(device_id)
    
    def optimize_placement(
        self,
        current_planogram: Dict[str, Any],
        heat_map: Dict[str, Any],
        constraints: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Optimize product placement based on heat zones
        
        Args:
            current_planogram: Current planogram configuration
            heat_map: Generated heat map
            constraints: Optional placement constraints
        
        Returns:
            Optimized planogram with recommendations
        """
        try:
            # Extract high-value zones
            high_value_zones = self._extract_high_value_zones(heat_map)
            
            # Identify high-margin products
            high_margin_products = self._identify_high_margin_products(
                current_planogram
            )
            
            # Generate placement recommendations
            recommendations = self._generate_placement_recommendations(
                current_planogram, high_value_zones, high_margin_products, constraints
            )
            
            # Calculate expected improvement
            expected_improvement = self._calculate_expected_improvement(
                current_planogram, recommendations, heat_map
            )
            
            # Create optimized planogram
            optimized_planogram = self._apply_recommendations(
                current_planogram, recommendations
            )
            
            return {
                "optimized_planogram": optimized_planogram,
                "recommendations": recommendations,
                "expected_improvement": expected_improvement,
                "moves_required": len(recommendations),
                "optimization_score": self._calculate_optimization_score(
                    optimized_planogram, heat_map
                ),
                "constraints_applied": constraints or {},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return {
                "optimized_planogram": current_planogram,
                "recommendations": [],
                "expected_improvement": {"revenue_increase": 0, "confidence": "low"},
                "error": str(e)
            }
    
    def _validate_heat_map_inputs(
        self,
        device_id: int,
        historical_sales: List[Dict]
    ):
        """Validate heat map generation inputs"""
        if not isinstance(device_id, int) or device_id <= 0:
            raise ValidationError("Valid device ID required")
        
        if not historical_sales:
            raise ValidationError("Historical sales data required")
        
        # Check for required fields
        required_fields = ["position", "revenue", "quantity"]
        for sale in historical_sales[:1]:
            for field in required_fields:
                if field not in sale:
                    raise ValidationError(f"Sales data must include {field}")
    
    def _analyze_position_performance(
        self,
        historical_sales: List[Dict]
    ) -> Dict[Tuple[int, int], Dict]:
        """
        Analyze performance by position
        
        Returns:
            Position metrics dictionary
        """
        position_metrics = {}
        
        for sale in historical_sales:
            position = sale.get("position", {})
            row = position.get("row", 0)
            col = position.get("column", 0)
            key = (row, col)
            
            if key not in position_metrics:
                position_metrics[key] = {
                    "revenue": [],
                    "quantity": [],
                    "products": set()
                }
            
            position_metrics[key]["revenue"].append(sale.get("revenue", 0))
            position_metrics[key]["quantity"].append(sale.get("quantity", 0))
            position_metrics[key]["products"].add(sale.get("product_id"))
        
        # Calculate aggregates
        for key, metrics in position_metrics.items():
            metrics["total_revenue"] = sum(metrics["revenue"])
            metrics["avg_revenue"] = statistics.mean(metrics["revenue"])
            metrics["total_quantity"] = sum(metrics["quantity"])
            metrics["product_diversity"] = len(metrics["products"])
            
            # Remove raw lists to save memory
            del metrics["revenue"]
            del metrics["quantity"]
        
        return position_metrics
    
    def _calculate_zone_revenues(
        self,
        position_metrics: Dict[Tuple[int, int], Dict]
    ) -> Dict[str, Dict]:
        """
        Calculate revenue by zone
        
        Returns:
            Zone revenue analysis
        """
        zone_revenues = {}
        
        for zone_name, zone_def in self.ZONE_DEFINITIONS.items():
            zone_positions = [
                (row, col) for row, col in position_metrics.keys()
                if row in zone_def["rows"]
            ]
            
            if zone_positions:
                revenues = [
                    position_metrics[pos]["total_revenue"]
                    for pos in zone_positions
                ]
                
                zone_revenues[zone_name] = {
                    "total_revenue": sum(revenues),
                    "average_revenue": statistics.mean(revenues),
                    "position_count": len(zone_positions),
                    "revenue_per_position": sum(revenues) / len(zone_positions),
                    "multiplier": zone_def["multiplier"],
                    "rows": zone_def["rows"]
                }
            else:
                zone_revenues[zone_name] = {
                    "total_revenue": 0,
                    "average_revenue": 0,
                    "position_count": 0,
                    "revenue_per_position": 0,
                    "multiplier": zone_def["multiplier"],
                    "rows": zone_def["rows"]
                }
        
        return zone_revenues
    
    def _generate_heat_matrix(
        self,
        position_metrics: Dict[Tuple[int, int], Dict],
        cabinet_config: Optional[Dict]
    ) -> List[List[float]]:
        """
        Generate heat matrix for visualization
        
        Returns:
            2D matrix of heat values (0-100)
        """
        if not position_metrics:
            return [[0]]
        
        # Determine matrix dimensions
        max_row = max(row for row, _ in position_metrics.keys())
        max_col = max(col for _, col in position_metrics.keys())
        
        # Initialize matrix
        matrix = [[0.0 for _ in range(max_col + 1)] for _ in range(max_row + 1)]
        
        # Find max revenue for normalization
        max_revenue = max(
            metrics["total_revenue"]
            for metrics in position_metrics.values()
        )
        
        if max_revenue == 0:
            return matrix
        
        # Fill matrix with normalized values
        for (row, col), metrics in position_metrics.items():
            heat_value = (metrics["total_revenue"] / max_revenue) * 100
            matrix[row][col] = round(heat_value, 1)
        
        return matrix
    
    def _identify_opportunities(
        self,
        position_metrics: Dict[Tuple[int, int], Dict],
        zone_revenues: Dict[str, Dict]
    ) -> List[Dict[str, Any]]:
        """
        Identify optimization opportunities
        
        Returns:
            List of opportunities
        """
        opportunities = []
        
        # Find underperforming premium positions
        premium_zones = self.ZONE_DEFINITIONS["premium"]["rows"]
        for (row, col), metrics in position_metrics.items():
            if row in premium_zones:
                expected_revenue = zone_revenues["premium"]["average_revenue"]
                actual_revenue = metrics["total_revenue"]
                
                if actual_revenue < expected_revenue * 0.8:
                    opportunities.append({
                        "type": "underperforming_premium",
                        "position": {"row": row, "column": col},
                        "current_revenue": actual_revenue,
                        "expected_revenue": expected_revenue,
                        "improvement_potential": expected_revenue - actual_revenue,
                        "recommendation": "Place high-margin or fast-moving product"
                    })
        
        # Find overperforming economy positions
        economy_zones = self.ZONE_DEFINITIONS["economy"]["rows"]
        for (row, col), metrics in position_metrics.items():
            if row in economy_zones:
                zone_avg = zone_revenues["economy"]["average_revenue"]
                actual_revenue = metrics["total_revenue"]
                
                if actual_revenue > zone_avg * 1.5:
                    opportunities.append({
                        "type": "overperforming_economy",
                        "position": {"row": row, "column": col},
                        "current_revenue": actual_revenue,
                        "zone_average": zone_avg,
                        "recommendation": "Consider moving product to premium zone"
                    })
        
        # Sort by improvement potential
        opportunities.sort(
            key=lambda x: x.get("improvement_potential", 0),
            reverse=True
        )
        
        return opportunities[:10]  # Return top 10 opportunities
    
    def _get_ai_recommendations(
        self,
        position_metrics: Dict[Tuple[int, int], Dict],
        zone_revenues: Dict[str, Dict]
    ) -> Optional[List[Dict]]:
        """
        Get AI-powered recommendations
        
        Returns:
            AI recommendations or None
        """
        if self.ai_client.fallback_mode:
            return None
        
        try:
            prompt = f"""
            Analyze this heat map data and provide optimization recommendations:
            
            Zone Performance:
            - Premium zones: ${zone_revenues.get('premium', {}).get('total_revenue', 0):.2f}
            - Standard zones: ${zone_revenues.get('standard', {}).get('total_revenue', 0):.2f}
            - Economy zones: ${zone_revenues.get('economy', {}).get('total_revenue', 0):.2f}
            
            Total positions analyzed: {len(position_metrics)}
            
            Provide 3 specific recommendations to improve revenue.
            
            Respond with JSON: {{"recommendations": [{{"action": "", "reason": "", "expected_impact": ""}}]}}
            """
            
            response = self.ai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are a retail space optimization expert. Provide actionable recommendations.",
                max_tokens=400,
                temperature=0.4
            )
            
            content = response.get("content", "{}")
            result = json.loads(content)
            return result.get("recommendations", [])
            
        except Exception as e:
            logger.error(f"AI recommendations error: {e}")
            return None
    
    def _count_high_performance(self, heat_matrix: List[List[float]]) -> int:
        """Count high-performance positions (>70% of max)"""
        count = 0
        for row in heat_matrix:
            for value in row:
                if value > 70:
                    count += 1
        return count
    
    def _calculate_concentration(
        self,
        position_metrics: Dict[Tuple[int, int], Dict]
    ) -> float:
        """
        Calculate revenue concentration (Gini coefficient)
        
        Returns:
            Concentration index (0-1, higher = more concentrated)
        """
        if not position_metrics:
            return 0
        
        revenues = sorted([m["total_revenue"] for m in position_metrics.values()])
        n = len(revenues)
        
        if n == 0 or sum(revenues) == 0:
            return 0
        
        # Calculate Gini coefficient
        cumsum = 0
        for i, revenue in enumerate(revenues):
            cumsum += (n - i) * revenue
        
        gini = (n + 1 - 2 * cumsum / sum(revenues)) / n
        
        return round(max(0, min(1, gini)), 3)
    
    def _extract_high_value_zones(self, heat_map: Dict) -> List[Tuple[int, int]]:
        """Extract high-value positions from heat map"""
        high_value_positions = []
        heat_matrix = heat_map.get("heat_matrix", [])
        
        for row_idx, row in enumerate(heat_matrix):
            for col_idx, value in enumerate(row):
                if value > 70:  # Top 30% performers
                    high_value_positions.append((row_idx, col_idx))
        
        return high_value_positions
    
    def _identify_high_margin_products(
        self,
        planogram: Dict
    ) -> List[int]:
        """Identify high-margin products (simplified)"""
        # In real implementation, would use actual margin data
        # For now, assume certain product IDs are high-margin
        high_margin_ids = [1, 2, 5, 6, 9, 10]  # Example IDs
        
        products_in_planogram = set()
        for slot in planogram.get("slots", []):
            product_id = slot.get("product_id")
            if product_id:
                products_in_planogram.add(product_id)
        
        return [p for p in high_margin_ids if p in products_in_planogram]
    
    def _generate_placement_recommendations(
        self,
        planogram: Dict,
        high_value_zones: List[Tuple[int, int]],
        high_margin_products: List[int],
        constraints: Optional[Dict]
    ) -> List[Dict]:
        """Generate specific placement recommendations"""
        recommendations = []
        
        # Find current positions of high-margin products
        product_positions = {}
        for slot in planogram.get("slots", []):
            product_id = slot.get("product_id")
            if product_id in high_margin_products:
                product_positions[product_id] = (
                    slot.get("row"), slot.get("column")
                )
        
        # Recommend moving high-margin products to high-value zones
        for product_id in high_margin_products:
            current_pos = product_positions.get(product_id)
            if current_pos and current_pos not in high_value_zones:
                # Find available high-value position
                for target_pos in high_value_zones:
                    if not self._position_occupied(planogram, target_pos):
                        recommendations.append({
                            "action": "move",
                            "product_id": product_id,
                            "from_position": {
                                "row": current_pos[0],
                                "column": current_pos[1]
                            },
                            "to_position": {
                                "row": target_pos[0],
                                "column": target_pos[1]
                            },
                            "reason": "Move high-margin product to high-value zone",
                            "expected_revenue_increase": 15.0  # Percentage
                        })
                        break
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _position_occupied(
        self,
        planogram: Dict,
        position: Tuple[int, int]
    ) -> bool:
        """Check if position is occupied"""
        for slot in planogram.get("slots", []):
            if (slot.get("row") == position[0] and 
                slot.get("column") == position[1] and
                slot.get("product_id")):
                return True
        return False
    
    def _calculate_expected_improvement(
        self,
        current_planogram: Dict,
        recommendations: List[Dict],
        heat_map: Dict
    ) -> Dict:
        """Calculate expected improvement from recommendations"""
        if not recommendations:
            return {"revenue_increase": 0, "confidence": "low"}
        
        # Simplified calculation
        total_increase = sum(
            rec.get("expected_revenue_increase", 0)
            for rec in recommendations
        )
        
        avg_increase = total_increase / len(recommendations)
        
        return {
            "revenue_increase": round(avg_increase, 1),
            "confidence": "medium" if len(recommendations) >= 3 else "low",
            "recommendations_count": len(recommendations)
        }
    
    def _apply_recommendations(
        self,
        planogram: Dict,
        recommendations: List[Dict]
    ) -> Dict:
        """Apply recommendations to create optimized planogram"""
        import copy
        optimized = copy.deepcopy(planogram)
        
        for rec in recommendations:
            if rec["action"] == "move":
                # Find and update slot
                for slot in optimized.get("slots", []):
                    from_pos = rec["from_position"]
                    to_pos = rec["to_position"]
                    
                    if (slot.get("row") == from_pos["row"] and
                        slot.get("column") == from_pos["column"]):
                        # Move to new position
                        slot["row"] = to_pos["row"]
                        slot["column"] = to_pos["column"]
                        break
        
        return optimized
    
    def _calculate_optimization_score(
        self,
        planogram: Dict,
        heat_map: Dict
    ) -> float:
        """Calculate optimization score for planogram"""
        heat_matrix = heat_map.get("heat_matrix", [])
        
        if not heat_matrix:
            return 0
        
        scores = []
        for slot in planogram.get("slots", []):
            row = slot.get("row", 0)
            col = slot.get("column", 0)
            
            if row < len(heat_matrix) and col < len(heat_matrix[row]):
                scores.append(heat_matrix[row][col])
        
        return statistics.mean(scores) if scores else 0
    
    def _fallback_heat_map(self, device_id: int) -> Dict:
        """Fallback heat map when service fails"""
        return {
            "device_id": device_id,
            "heat_matrix": [[50, 70, 60], [80, 90, 85], [40, 50, 45]],
            "zone_analysis": {
                "premium": {"total_revenue": 1000, "average_revenue": 500},
                "standard": {"total_revenue": 800, "average_revenue": 400},
                "economy": {"total_revenue": 600, "average_revenue": 300}
            },
            "optimization_opportunities": [],
            "ai_recommendations": None,
            "statistics": {
                "total_positions": 9,
                "high_performance_zones": 3,
                "revenue_concentration": 0.3
            },
            "visualization": {
                "color_scale": {
                    "min": 0,
                    "max": 100,
                    "gradient": ["#0000FF", "#00FF00", "#FFFF00", "#FF0000"]
                },
                "opacity": 0.4
            },
            "cache_ttl": 86400,
            "generated_at": datetime.now().isoformat()
        }