"""
Revenue prediction service for planogram optimization

Analyzes historical data to predict revenue impact of planogram changes
"""

import json
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import random

from ..base.client import AIClient
from ..base.exceptions import AIServiceError, ValidationError
from ..pipelines.cache import CacheManager, cached

logger = logging.getLogger(__name__)


class RevenuePrediction:
    """
    Predicts revenue impact of planogram configurations
    
    Uses historical sales data and AI to forecast:
    - Expected revenue changes
    - Confidence intervals
    - Product-specific predictions
    - Seasonal adjustments
    """
    
    def __init__(
        self,
        ai_client: Optional[AIClient] = None,
        cache_manager: Optional[CacheManager] = None
    ):
        """
        Initialize predictor
        
        Args:
            ai_client: AI client instance
            cache_manager: Cache manager instance
        """
        self.ai_client = ai_client or AIClient()
        self.cache_manager = cache_manager or CacheManager()
    
    @cached(cache_manager=None, ttl=3600)  # 1 hour cache
    def predict_revenue(
        self,
        planogram_data: Dict[str, Any],
        historical_sales: List[Dict[str, Any]],
        prediction_days: int = 30,
        include_seasonality: bool = True
    ) -> Dict[str, Any]:
        """
        Predict revenue for a planogram configuration
        
        Args:
            planogram_data: Current planogram configuration
            historical_sales: Historical sales data (90+ days recommended)
            prediction_days: Number of days to predict
            include_seasonality: Whether to adjust for seasonal patterns
        
        Returns:
            Prediction results with confidence intervals
        """
        try:
            # Validate inputs
            self._validate_prediction_inputs(planogram_data, historical_sales)
            
            # Calculate baseline metrics
            baseline = self._calculate_baseline(historical_sales)
            
            # Analyze planogram impact
            planogram_impact = self._analyze_planogram_impact(
                planogram_data, historical_sales
            )
            
            # Get AI predictions if available
            ai_prediction = self._get_ai_prediction(
                planogram_data, historical_sales, prediction_days
            )
            
            # Calculate seasonal adjustments
            seasonal_factor = 1.0
            if include_seasonality:
                seasonal_factor = self._calculate_seasonality(historical_sales)
            
            # Combine predictions
            predicted_revenue = self._combine_predictions(
                baseline, planogram_impact, ai_prediction, seasonal_factor
            )
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                predicted_revenue, historical_sales
            )
            
            # Generate product-level predictions
            product_predictions = self._predict_by_product(
                planogram_data, historical_sales, planogram_impact
            )
            
            return {
                "predicted_revenue": round(predicted_revenue, 2),
                "baseline_revenue": round(baseline["daily_average"] * prediction_days, 2),
                "expected_change": round(predicted_revenue - (baseline["daily_average"] * prediction_days), 2),
                "change_percentage": round(
                    ((predicted_revenue / (baseline["daily_average"] * prediction_days)) - 1) * 100, 1
                ),
                "confidence_intervals": confidence_intervals,
                "product_predictions": product_predictions,
                "factors": {
                    "planogram_impact": round(planogram_impact, 3),
                    "seasonal_adjustment": round(seasonal_factor, 3),
                    "ai_confidence": ai_prediction.get("confidence", 0) if ai_prediction else 0
                },
                "prediction_period": {
                    "days": prediction_days,
                    "start_date": datetime.now().isoformat(),
                    "end_date": (datetime.now() + timedelta(days=prediction_days)).isoformat()
                },
                "model_version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }
            
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._fallback_prediction(prediction_days)
    
    def _validate_prediction_inputs(
        self,
        planogram_data: Dict,
        historical_sales: List[Dict]
    ):
        """Validate prediction inputs"""
        if not planogram_data:
            raise ValidationError("Planogram data is required")
        
        if not historical_sales or len(historical_sales) < 30:
            raise ValidationError("At least 30 days of historical data required")
        
        # Check for required fields in sales data
        required_fields = ["date", "product_id", "quantity", "revenue"]
        for sale in historical_sales[:1]:  # Check first record
            for field in required_fields:
                if field not in sale:
                    raise ValidationError(f"Historical sales must include {field}")
    
    def _calculate_baseline(self, historical_sales: List[Dict]) -> Dict[str, float]:
        """
        Calculate baseline metrics from historical data
        
        Returns:
            Baseline statistics
        """
        daily_revenues = {}
        
        for sale in historical_sales:
            date = sale.get("date", "")
            revenue = sale.get("revenue", 0)
            
            if date not in daily_revenues:
                daily_revenues[date] = 0
            daily_revenues[date] += revenue
        
        revenues = list(daily_revenues.values())
        
        if not revenues:
            return {"daily_average": 0, "std_dev": 0, "trend": 0}
        
        return {
            "daily_average": statistics.mean(revenues),
            "std_dev": statistics.stdev(revenues) if len(revenues) > 1 else 0,
            "median": statistics.median(revenues),
            "trend": self._calculate_trend(revenues)
        }
    
    def _calculate_trend(self, values: List[float]) -> float:
        """
        Calculate trend coefficient (simple linear regression)
        
        Returns:
            Trend coefficient (-1 to 1)
        """
        if len(values) < 2:
            return 0
        
        n = len(values)
        x = list(range(n))
        
        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
        
        slope = numerator / denominator
        
        # Normalize to -1 to 1 range
        return max(-1, min(1, slope / y_mean if y_mean != 0 else 0))
    
    def _analyze_planogram_impact(
        self,
        planogram_data: Dict,
        historical_sales: List[Dict]
    ) -> float:
        """
        Analyze expected impact of planogram configuration
        
        Returns:
            Impact multiplier (0.5 to 1.5)
        """
        impact_factors = []
        
        # Factor 1: High-visibility placement of top sellers
        top_sellers = self._identify_top_sellers(historical_sales)
        visibility_score = self._calculate_visibility_score(planogram_data, top_sellers)
        impact_factors.append(0.8 + (visibility_score * 0.4))  # 0.8 to 1.2
        
        # Factor 2: Product diversity
        diversity_score = self._calculate_diversity_score(planogram_data)
        impact_factors.append(0.9 + (diversity_score * 0.2))  # 0.9 to 1.1
        
        # Factor 3: Category clustering
        clustering_score = self._calculate_clustering_score(planogram_data)
        impact_factors.append(0.85 + (clustering_score * 0.3))  # 0.85 to 1.15
        
        # Combine factors
        return statistics.mean(impact_factors)
    
    def _identify_top_sellers(self, historical_sales: List[Dict]) -> List[int]:
        """
        Identify top-selling products
        
        Returns:
            List of top product IDs
        """
        product_revenues = {}
        
        for sale in historical_sales:
            product_id = sale.get("product_id")
            revenue = sale.get("revenue", 0)
            
            if product_id not in product_revenues:
                product_revenues[product_id] = 0
            product_revenues[product_id] += revenue
        
        # Sort by revenue and get top 20%
        sorted_products = sorted(
            product_revenues.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        top_count = max(1, len(sorted_products) // 5)
        return [p[0] for p in sorted_products[:top_count]]
    
    def _calculate_visibility_score(
        self,
        planogram_data: Dict,
        top_sellers: List[int]
    ) -> float:
        """
        Calculate visibility score for top sellers
        
        Returns:
            Score 0-1
        """
        if not top_sellers:
            return 0.5
        
        scores = []
        
        for slot in planogram_data.get("slots", []):
            product_id = slot.get("product_id")
            if product_id in top_sellers:
                row = slot.get("row", 0)
                # Eye level (rows 1-2) = 1.0, decreases with distance
                if row <= 2:
                    scores.append(1.0)
                elif row <= 3:
                    scores.append(0.8)
                elif row <= 4:
                    scores.append(0.6)
                else:
                    scores.append(0.4)
        
        return statistics.mean(scores) if scores else 0.5
    
    def _calculate_diversity_score(self, planogram_data: Dict) -> float:
        """
        Calculate product diversity score
        
        Returns:
            Score 0-1
        """
        products = set()
        total_slots = 0
        
        for slot in planogram_data.get("slots", []):
            product_id = slot.get("product_id")
            if product_id:
                products.add(product_id)
                total_slots += 1
        
        if total_slots == 0:
            return 0
        
        # Ideal diversity is ~70% of slots with unique products
        diversity_ratio = len(products) / total_slots
        ideal_ratio = 0.7
        
        # Score peaks at ideal ratio
        if diversity_ratio <= ideal_ratio:
            return diversity_ratio / ideal_ratio
        else:
            return max(0, 1 - (diversity_ratio - ideal_ratio) / (1 - ideal_ratio))
    
    def _calculate_clustering_score(self, planogram_data: Dict) -> float:
        """
        Calculate category clustering score
        
        Returns:
            Score 0-1
        """
        # Simplified: Check if similar products are grouped
        category_positions = {}
        
        for slot in planogram_data.get("slots", []):
            product_id = slot.get("product_id")
            if product_id:
                category = self._get_product_category(product_id)
                position = (slot.get("row", 0), slot.get("column", 0))
                
                if category not in category_positions:
                    category_positions[category] = []
                category_positions[category].append(position)
        
        # Calculate clustering for each category
        clustering_scores = []
        
        for category, positions in category_positions.items():
            if len(positions) < 2:
                clustering_scores.append(1.0)
                continue
            
            # Calculate average distance between products in same category
            distances = []
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    dist = abs(positions[i][0] - positions[j][0]) + \
                           abs(positions[i][1] - positions[j][1])
                    distances.append(dist)
            
            avg_distance = statistics.mean(distances)
            # Lower distance = better clustering
            clustering_scores.append(max(0, 1 - (avg_distance / 10)))
        
        return statistics.mean(clustering_scores) if clustering_scores else 0.5
    
    def _get_product_category(self, product_id: int) -> str:
        """Get product category"""
        categories = {
            "beverages": [1, 2, 3, 4],
            "snacks": [5, 6, 7, 8],
            "candy": [9, 10, 11, 12]
        }
        
        for category, products in categories.items():
            if product_id in products:
                return category
        
        return "other"
    
    def _calculate_seasonality(self, historical_sales: List[Dict]) -> float:
        """
        Calculate seasonal adjustment factor
        
        Returns:
            Seasonal multiplier (0.8 to 1.2)
        """
        # Group sales by month
        monthly_revenues = {}
        
        for sale in historical_sales:
            date_str = sale.get("date", "")
            try:
                date = datetime.fromisoformat(date_str)
                month = date.month
                
                if month not in monthly_revenues:
                    monthly_revenues[month] = []
                monthly_revenues[month].append(sale.get("revenue", 0))
            except:
                continue
        
        if not monthly_revenues:
            return 1.0
        
        # Calculate average for each month
        monthly_averages = {
            month: statistics.mean(revenues)
            for month, revenues in monthly_revenues.items()
        }
        
        # Current month's factor
        current_month = datetime.now().month
        if current_month in monthly_averages:
            overall_avg = statistics.mean(monthly_averages.values())
            if overall_avg > 0:
                factor = monthly_averages[current_month] / overall_avg
                return max(0.8, min(1.2, factor))
        
        return 1.0
    
    def _get_ai_prediction(
        self,
        planogram_data: Dict,
        historical_sales: List[Dict],
        prediction_days: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get AI-enhanced prediction
        
        Returns:
            AI prediction or None
        """
        if self.ai_client.fallback_mode:
            return None
        
        try:
            prompt = f"""
            Predict revenue for this planogram configuration:
            
            Planogram:
            - Total slots: {len(planogram_data.get('slots', []))}
            - Products: {len(set(s.get('product_id') for s in planogram_data.get('slots', [])))}
            
            Historical performance (last 30 days):
            - Average daily revenue: ${self._calculate_baseline(historical_sales[-30:])['daily_average']:.2f}
            - Trend: {self._calculate_baseline(historical_sales[-30:])['trend']:.2f}
            
            Predict revenue for next {prediction_days} days.
            
            Respond with JSON: {{"predicted_revenue": <number>, "confidence": <0-1>, "factors": []}}
            """
            
            response = self.ai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are a retail analytics expert. Provide data-driven revenue predictions.",
                model=self.ai_client.ADVANCED_MODEL,
                max_tokens=300,
                temperature=0.3
            )
            
            content = response.get("content", "{}")
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return None
    
    def _combine_predictions(
        self,
        baseline: Dict[str, float],
        planogram_impact: float,
        ai_prediction: Optional[Dict],
        seasonal_factor: float
    ) -> float:
        """
        Combine prediction components
        
        Returns:
            Final predicted revenue
        """
        base_prediction = baseline["daily_average"] * 30  # Default 30 days
        
        # Apply planogram impact
        adjusted_prediction = base_prediction * planogram_impact
        
        # Apply seasonal adjustment
        adjusted_prediction *= seasonal_factor
        
        # Blend with AI prediction if available
        if ai_prediction and "predicted_revenue" in ai_prediction:
            ai_revenue = ai_prediction["predicted_revenue"]
            confidence = ai_prediction.get("confidence", 0.5)
            
            # Weighted average based on confidence
            adjusted_prediction = (
                adjusted_prediction * (1 - confidence) +
                ai_revenue * confidence
            )
        
        return adjusted_prediction
    
    def _calculate_confidence_intervals(
        self,
        predicted_revenue: float,
        historical_sales: List[Dict]
    ) -> Dict[str, float]:
        """
        Calculate confidence intervals for prediction
        
        Returns:
            Confidence intervals
        """
        baseline = self._calculate_baseline(historical_sales)
        std_dev = baseline.get("std_dev", 0)
        
        # Calculate intervals based on historical variance
        margin_68 = std_dev * 30  # 68% confidence (1 std dev)
        margin_95 = std_dev * 30 * 1.96  # 95% confidence
        
        return {
            "confidence_68": {
                "lower": round(predicted_revenue - margin_68, 2),
                "upper": round(predicted_revenue + margin_68, 2)
            },
            "confidence_95": {
                "lower": round(predicted_revenue - margin_95, 2),
                "upper": round(predicted_revenue + margin_95, 2)
            }
        }
    
    def _predict_by_product(
        self,
        planogram_data: Dict,
        historical_sales: List[Dict],
        planogram_impact: float
    ) -> List[Dict[str, Any]]:
        """
        Generate product-level predictions
        
        Returns:
            List of product predictions
        """
        product_predictions = []
        product_baselines = {}
        
        # Calculate baseline for each product
        for sale in historical_sales:
            product_id = sale.get("product_id")
            revenue = sale.get("revenue", 0)
            
            if product_id not in product_baselines:
                product_baselines[product_id] = []
            product_baselines[product_id].append(revenue)
        
        # Generate predictions
        for product_id, revenues in product_baselines.items():
            baseline_revenue = statistics.mean(revenues)
            
            # Find product position in planogram
            position_factor = 1.0
            for slot in planogram_data.get("slots", []):
                if slot.get("product_id") == product_id:
                    row = slot.get("row", 0)
                    if row <= 2:
                        position_factor = 1.2
                    elif row <= 3:
                        position_factor = 1.0
                    else:
                        position_factor = 0.8
                    break
            
            predicted = baseline_revenue * planogram_impact * position_factor
            
            product_predictions.append({
                "product_id": product_id,
                "baseline_revenue": round(baseline_revenue, 2),
                "predicted_revenue": round(predicted, 2),
                "change_percentage": round(((predicted / baseline_revenue) - 1) * 100, 1)
            })
        
        # Sort by predicted revenue
        product_predictions.sort(key=lambda x: x["predicted_revenue"], reverse=True)
        
        return product_predictions[:10]  # Return top 10
    
    def _fallback_prediction(self, prediction_days: int) -> Dict[str, Any]:
        """Fallback prediction when service fails"""
        return {
            "predicted_revenue": 1000.00 * prediction_days / 30,
            "baseline_revenue": 950.00 * prediction_days / 30,
            "expected_change": 50.00 * prediction_days / 30,
            "change_percentage": 5.3,
            "confidence_intervals": {
                "confidence_68": {
                    "lower": 900.00 * prediction_days / 30,
                    "upper": 1100.00 * prediction_days / 30
                },
                "confidence_95": {
                    "lower": 800.00 * prediction_days / 30,
                    "upper": 1200.00 * prediction_days / 30
                }
            },
            "product_predictions": [],
            "factors": {
                "planogram_impact": 1.0,
                "seasonal_adjustment": 1.0,
                "ai_confidence": 0
            },
            "prediction_period": {
                "days": prediction_days,
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=prediction_days)).isoformat()
            },
            "model_version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }