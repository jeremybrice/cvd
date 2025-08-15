# AI Planogram Enhancement Testing Strategy

## Executive Summary
This comprehensive testing strategy ensures quality, reliability, and performance for all 7 AI features in the planogram enhancement system. The strategy covers unit testing, integration testing, end-to-end testing, performance benchmarking, AI accuracy validation, A/B testing framework, and regression test suites.

## Test Strategy Overview

### Testing Principles
1. **Parallel Development**: Tests written alongside feature implementation
2. **Context-Driven**: Adapt testing approach based on AI service requirements
3. **Data-Driven**: Comprehensive test data covering edge cases
4. **Performance-First**: Validate response times and resource usage
5. **AI Validation**: Verify accuracy, confidence scores, and business impact

### Testing Layers
```
┌─────────────────────────────────────────────────┐
│           E2E Tests (User Workflows)            │
├─────────────────────────────────────────────────┤
│         Integration Tests (API Layer)           │
├─────────────────────────────────────────────────┤
│          Unit Tests (AI Services)               │
├─────────────────────────────────────────────────┤
│    Performance & Load Testing (All Layers)      │
└─────────────────────────────────────────────────┘
```

## 1. Real-Time Planogram Assistant Testing

### Unit Tests (`test_realtime_assistant.py`)

```python
import unittest
from unittest.mock import Mock, patch
from ai_services.realtime_assistant import RealtimePlanogramAssistant

class TestRealtimeAssistant(unittest.TestCase):
    
    def setUp(self):
        self.assistant = RealtimePlanogramAssistant(api_key="test_key")
        self.test_context = {
            'device_id': 1,
            'cabinet_index': 0,
            'cabinet_type': 'Cooler',
            'rows': 5,
            'columns': 8,
            'current_products': [1, 2, 3, 4],
            'sales_data': [...],
            'constraints': {
                'temperature_zones': {'frozen': ['A1-A8'], 'cold': ['B1-E8']},
                'weight_limits': {'bottom_row': 50}
            }
        }
    
    def test_placement_scoring_valid_placement(self):
        """Test scoring for valid product placement"""
        score = self.assistant.analyze_placement(
            product_id=1,
            slot_position='B3',
            context=self.test_context
        )
        
        self.assertIsInstance(score, dict)
        self.assertIn('score', score)
        self.assertIn('feedback', score)
        self.assertTrue(0 <= score['score'] <= 100)
        self.assertIsInstance(score['feedback'], str)
    
    def test_constraint_validation(self):
        """Test real-time constraint checking"""
        # Test frozen product in wrong zone
        result = self.assistant.validate_constraints(
            product_id=10,  # Frozen product
            slot_position='E8',  # Non-frozen zone
            context=self.test_context
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('temperature', result['violations'])
    
    def test_response_time_requirement(self):
        """Test that responses meet <500ms requirement"""
        import time
        
        start = time.time()
        self.assistant.analyze_placement(1, 'A1', self.test_context)
        duration = (time.time() - start) * 1000
        
        self.assertLess(duration, 500, "Response time exceeds 500ms requirement")
    
    @patch('anthropic.Anthropic')
    def test_haiku_model_usage(self, mock_anthropic):
        """Verify Haiku model is used for speed"""
        self.assistant.analyze_placement(1, 'A1', self.test_context)
        
        mock_anthropic.return_value.messages.create.assert_called_with(
            model='claude-3-haiku-20240307',
            max_tokens=500,
            temperature=0.3
        )
```

### Integration Tests (`test_realtime_assistant_api.py`)

```python
import json
import unittest
from app import app

class TestRealtimeAssistantAPI(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Login as admin
        self.login_as_admin()
    
    def test_analyze_placement_endpoint(self):
        """Test /api/planogram/analyze endpoint"""
        payload = {
            'product_id': 1,
            'slot_position': 'B3',
            'device_id': 1,
            'cabinet_index': 0
        }
        
        response = self.app.post('/api/planogram/analyze',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('score', data)
        self.assertIn('feedback', data)
        self.assertIn('suggestions', data)
    
    def test_batch_analysis(self):
        """Test analyzing multiple placements"""
        payload = {
            'placements': [
                {'product_id': 1, 'slot_position': 'A1'},
                {'product_id': 2, 'slot_position': 'A2'},
                {'product_id': 3, 'slot_position': 'B1'}
            ],
            'device_id': 1,
            'cabinet_index': 0
        }
        
        response = self.app.post('/api/planogram/analyze-batch',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['results']), 3)
```

### E2E Tests (`test_realtime_assistant_e2e.py`)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestRealtimeAssistantE2E(unittest.TestCase):
    
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000")
        self.login_as_admin()
        self.navigate_to_planogram()
    
    def test_drag_drop_with_ai_feedback(self):
        """Test drag-and-drop with real-time AI feedback"""
        # Find product in catalog
        product = self.driver.find_element(By.CSS_SELECTOR, 
                                          "[data-product-id='1']")
        
        # Find target slot
        slot = self.driver.find_element(By.CSS_SELECTOR, 
                                       "[data-slot-position='B3']")
        
        # Start drag
        action = webdriver.ActionChains(self.driver)
        action.click_and_hold(product)
        action.move_to_element(slot)
        
        # Wait for AI feedback to appear
        feedback = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ai-feedback"))
        )
        
        # Verify feedback is visible
        self.assertTrue(feedback.is_displayed())
        
        # Check score indicator
        score_element = feedback.find_element(By.CLASS_NAME, "placement-score")
        score = int(score_element.text)
        self.assertTrue(0 <= score <= 100)
        
        # Complete drop
        action.release()
        action.perform()
```

### Test Data Requirements

```python
# test_data/realtime_assistant_data.py
TEST_SCENARIOS = {
    'optimal_placement': {
        'product': {'id': 1, 'name': 'Coke', 'category': 'Beverages'},
        'slot': 'B3',  # Eye level, center
        'expected_score': range(85, 100),
        'expected_feedback': 'Excellent placement'
    },
    'suboptimal_placement': {
        'product': {'id': 1, 'name': 'Coke', 'category': 'Beverages'},
        'slot': 'E1',  # Bottom corner
        'expected_score': range(40, 60),
        'expected_feedback': 'Consider higher visibility'
    },
    'constraint_violation': {
        'product': {'id': 10, 'name': 'Ice Cream', 'category': 'Frozen'},
        'slot': 'E8',  # Non-frozen zone
        'expected_score': 0,
        'expected_feedback': 'Temperature zone violation'
    }
}
```

### Acceptance Criteria
- [ ] Response time < 500ms for 95% of requests
- [ ] Placement scores between 0-100
- [ ] Clear, actionable feedback messages
- [ ] Constraint violations prevent placement
- [ ] Visual indicators update in real-time
- [ ] Batch analysis handles 40 slots efficiently

## 2. Revenue Prediction Engine Testing

### Unit Tests (`test_revenue_predictor.py`)

```python
class TestRevenuePrediction(unittest.TestCase):
    
    def setUp(self):
        self.predictor = PlanogramRevenuePredictor(db_path='test.db')
        self.setup_test_database()
    
    def test_baseline_calculation(self):
        """Test accurate baseline revenue calculation"""
        baseline = self.predictor.calculate_baseline_revenue(
            self.current_planogram
        )
        
        # Based on 30-day historical average
        expected = 150.00  # $5/day * 30 days
        self.assertAlmostEqual(baseline, expected, places=2)
    
    def test_prediction_with_confidence(self):
        """Test revenue prediction with confidence intervals"""
        result = self.predictor.predict_revenue_impact(
            self.current_planogram,
            self.proposed_planogram
        )
        
        self.assertIn('predicted_revenue', result)
        self.assertIn('confidence_interval', result)
        self.assertIn('lift_percentage', result)
        
        # Confidence interval should be tuple (lower, upper)
        ci = result['confidence_interval']
        self.assertIsInstance(ci, tuple)
        self.assertLess(ci[0], result['predicted_revenue'])
        self.assertGreater(ci[1], result['predicted_revenue'])
    
    def test_break_even_analysis(self):
        """Test break-even calculation for changes"""
        result = self.predictor.predict_revenue_impact(
            self.current_planogram,
            self.new_product_planogram
        )
        
        self.assertIn('break_even_days', result)
        self.assertIsInstance(result['break_even_days'], (int, float))
        
    def test_risk_factor_identification(self):
        """Test identification of risk factors"""
        risks = self.predictor.identify_risks(
            self.current_planogram,
            self.risky_planogram
        )
        
        self.assertIsInstance(risks, list)
        for risk in risks:
            self.assertIn('factor', risk)
            self.assertIn('severity', risk)
            self.assertIn('mitigation', risk)
```

### Integration Tests (`test_revenue_predictor_api.py`)

```python
class TestRevenuePredictionAPI(unittest.TestCase):
    
    def test_predict_endpoint(self):
        """Test /api/planogram/predict endpoint"""
        payload = {
            'device_id': 1,
            'cabinet_index': 0,
            'proposed_changes': [
                {'slot': 'A1', 'product_id': 5},
                {'slot': 'B2', 'product_id': 6}
            ]
        }
        
        response = self.app.post('/api/planogram/predict',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify prediction structure
        self.assertIn('current_revenue', data)
        self.assertIn('predicted_revenue', data)
        self.assertIn('lift_percentage', data)
        self.assertIn('confidence', data)
        self.assertIn('break_even_days', data)
```

### Test Data Requirements

```python
# test_data/revenue_predictor_data.py
PREDICTION_SCENARIOS = {
    'high_confidence': {
        'data_points': 90,  # 90 days of data
        'expected_confidence': 0.85,
        'confidence_interval_width': 0.1  # ±10%
    },
    'low_confidence': {
        'data_points': 7,  # Only 7 days
        'expected_confidence': 0.45,
        'confidence_interval_width': 0.3  # ±30%
    },
    'new_product': {
        'historical_data': None,
        'similar_products': [1, 2, 3],
        'expected_method': 'similarity_based'
    }
}
```

### Acceptance Criteria
- [ ] Predictions within 15% of actual (with 30+ days data)
- [ ] Confidence intervals contain actual 85% of time
- [ ] Break-even calculation accurate within 2 days
- [ ] Risk factors identified for all major changes
- [ ] API response time < 7 seconds for full analysis

## 3. Visual Heat Zone Analysis Testing

### Unit Tests (`test_heat_zone_analysis.py`)

```python
class TestHeatZoneAnalysis(unittest.TestCase):
    
    def setUp(self):
        self.analyzer = VisualHeatZoneAnalyzer()
    
    def test_zone_value_calculation(self):
        """Test zone value multiplier calculation"""
        # Eye level center should have highest value
        value_b3 = self.analyzer.get_zone_value('B', 3)
        value_e1 = self.analyzer.get_zone_value('E', 1)
        
        self.assertGreater(value_b3, value_e1)
        self.assertAlmostEqual(value_b3, 1.4, places=1)
        self.assertAlmostEqual(value_e1, 0.7, places=1)
    
    def test_heat_map_generation(self):
        """Test heat map data generation"""
        heat_map = self.analyzer.generate_heat_map(
            rows=5, 
            columns=8,
            sales_data=self.sales_data
        )
        
        self.assertEqual(len(heat_map), 40)  # 5*8 slots
        
        for slot in heat_map:
            self.assertIn('position', slot)
            self.assertIn('value', slot)
            self.assertIn('color', slot)
            self.assertTrue(0 <= slot['value'] <= 2.0)
    
    def test_accessibility_scoring(self):
        """Test accessibility scores for heavy items"""
        # Heavy item should score low in top row
        score_top = self.analyzer.score_accessibility(
            product_weight=25,  # lbs
            slot_position='A1'
        )
        
        # Heavy item should score high in bottom row
        score_bottom = self.analyzer.score_accessibility(
            product_weight=25,
            slot_position='E1'
        )
        
        self.assertLess(score_top, 0.5)
        self.assertGreater(score_bottom, 0.8)
```

### Visual Testing (`test_heat_zone_visual.py`)

```python
from PIL import Image
import numpy as np

class TestHeatZoneVisualization(unittest.TestCase):
    
    def test_heat_map_rendering(self):
        """Test visual heat map rendering"""
        heat_map_data = self.analyzer.generate_heat_map(5, 8, self.sales_data)
        image = self.analyzer.render_heat_map(heat_map_data)
        
        # Verify image properties
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.size, (800, 500))  # Expected dimensions
        
        # Verify color gradient
        pixels = np.array(image)
        red_channel = pixels[:, :, 0]
        
        # High value zones should be more red
        top_center = red_channel[100:200, 350:450].mean()
        bottom_corner = red_channel[400:500, 0:100].mean()
        self.assertGreater(top_center, bottom_corner)
```

### Acceptance Criteria
- [ ] Zone multipliers correctly applied (1.8x for prime zones)
- [ ] Heat map visualization renders correctly
- [ ] Accessibility scores prevent poor placements
- [ ] Category clustering effectiveness measured
- [ ] Revenue improvement of $3-5/day per cabinet

## 4. Product Affinity Clustering Testing

### Unit Tests (`test_affinity_engine.py`)

```python
class TestAffinityEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = ProductAffinityAnalyzer(db_path='test.db')
        self.load_transaction_data()
    
    def test_affinity_matrix_calculation(self):
        """Test product correlation matrix generation"""
        matrix = self.engine.calculate_affinity_matrix(
            self.transaction_data
        )
        
        # Matrix should be symmetric
        self.assertEqual(matrix.shape[0], matrix.shape[1])
        
        # Diagonal should be 1.0 (product with itself)
        for i in range(matrix.shape[0]):
            self.assertAlmostEqual(matrix[i][i], 1.0)
        
        # Known correlations from test data
        coke_pepsi = matrix[1][2]  # Should be negative (substitutes)
        chips_salsa = matrix[4][5]  # Should be positive (complements)
        
        self.assertLess(coke_pepsi, 0)
        self.assertGreater(chips_salsa, 0.5)
    
    def test_lift_score_calculation(self):
        """Test lift score for product pairs"""
        lift = self.engine.calculate_lift(
            product_a=4,  # Chips
            product_b=5,  # Salsa
            transactions=self.transaction_data
        )
        
        # Lift > 1 indicates positive correlation
        self.assertGreater(lift, 1.0)
        
    def test_cluster_recommendations(self):
        """Test clustering recommendations"""
        clusters = self.engine.recommend_clusters(
            current_planogram=self.planogram,
            min_support=0.1,
            min_confidence=0.5
        )
        
        self.assertIsInstance(clusters, list)
        for cluster in clusters:
            self.assertIn('products', cluster)
            self.assertIn('support', cluster)
            self.assertIn('confidence', cluster)
            self.assertIn('lift', cluster)
            self.assertGreaterEqual(cluster['confidence'], 0.5)
```

### Integration Tests (`test_affinity_api.py`)

```python
class TestAffinityAPI(unittest.TestCase):
    
    def test_affinity_analysis_endpoint(self):
        """Test /api/planogram/affinity endpoint"""
        response = self.app.get('/api/planogram/affinity?device_id=1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('affinity_matrix', data)
        self.assertIn('recommended_clusters', data)
        self.assertIn('cross_sell_opportunities', data)
```

### Test Data Requirements

```python
# test_data/affinity_data.py
TRANSACTION_PATTERNS = {
    'complementary': [
        {'products': [4, 5], 'frequency': 0.7},  # Chips + Salsa
        {'products': [1, 3], 'frequency': 0.5},  # Coke + Snickers
    ],
    'substitute': [
        {'products': [1, 2], 'frequency': 0.1},  # Coke OR Pepsi
    ],
    'impulse': [
        {'products': [3, 7, 8], 'frequency': 0.3},  # Candy items
    ]
}
```

### Acceptance Criteria
- [ ] Affinity matrix accurately reflects purchase patterns
- [ ] Lift scores > 1.0 for complementary products
- [ ] Clustering increases average transaction by 8-12%
- [ ] API returns recommendations in < 3 seconds
- [ ] Support and confidence thresholds configurable

## 5. Dynamic Demand Forecasting Testing

### Unit Tests (`test_demand_forecaster.py`)

```python
class TestDemandForecaster(unittest.TestCase):
    
    def setUp(self):
        self.forecaster = DemandForecaster(db_path='test.db')
        
    def test_seasonal_pattern_detection(self):
        """Test detection of seasonal patterns"""
        patterns = self.forecaster.detect_patterns(
            product_id=1,
            time_period=90  # days
        )
        
        self.assertIn('weekly', patterns)
        self.assertIn('monthly', patterns)
        
        # Monday should show different pattern than Friday
        monday_avg = patterns['weekly']['monday']
        friday_avg = patterns['weekly']['friday']
        self.assertNotAlmostEqual(monday_avg, friday_avg, places=1)
    
    def test_weather_correlation(self):
        """Test weather impact on demand"""
        correlation = self.forecaster.calculate_weather_impact(
            product_id=2,  # Cold beverage
            weather_data=self.weather_data
        )
        
        # Cold beverages should correlate with temperature
        self.assertGreater(correlation['temperature'], 0.3)
        
    def test_demand_prediction_accuracy(self):
        """Test prediction accuracy with historical data"""
        # Use 60 days for training, 30 for testing
        predictions = self.forecaster.predict_demand(
            product_id=1,
            forecast_days=30,
            training_days=60
        )
        
        # Compare with actual
        actual = self.get_actual_demand(product_id=1, days=30)
        mape = self.calculate_mape(predictions, actual)
        
        # Mean Absolute Percentage Error should be < 20%
        self.assertLess(mape, 0.20)
    
    def test_stockout_prediction(self):
        """Test stockout risk prediction"""
        risk = self.forecaster.predict_stockout_risk(
            product_id=1,
            current_stock=10,
            days_ahead=7
        )
        
        self.assertIn('probability', risk)
        self.assertIn('expected_stockout_day', risk)
        self.assertIn('recommended_reorder', risk)
        
        self.assertTrue(0 <= risk['probability'] <= 1)
```

### Performance Tests (`test_demand_forecaster_performance.py`)

```python
class TestDemandForecasterPerformance(unittest.TestCase):
    
    def test_bulk_prediction_performance(self):
        """Test performance for multiple products"""
        import time
        
        product_ids = list(range(1, 13))  # All 12 products
        
        start = time.time()
        for product_id in product_ids:
            self.forecaster.predict_demand(
                product_id=product_id,
                forecast_days=7
            )
        duration = time.time() - start
        
        # Should process all products in < 5 seconds
        self.assertLess(duration, 5.0)
    
    def test_model_training_time(self):
        """Test model training performance"""
        import time
        
        start = time.time()
        self.forecaster.train_model(
            product_id=1,
            training_days=90
        )
        duration = time.time() - start
        
        # Model training should complete in < 2 seconds
        self.assertLess(duration, 2.0)
```

### Test Data Requirements

```python
# test_data/demand_forecast_data.py
FORECAST_SCENARIOS = {
    'stable_demand': {
        'pattern': 'constant',
        'daily_units': 10,
        'variance': 0.1,
        'expected_mape': 0.05
    },
    'weekly_pattern': {
        'pattern': 'weekly',
        'monday': 5,
        'friday': 15,
        'weekend': 20,
        'expected_mape': 0.15
    },
    'seasonal_pattern': {
        'pattern': 'seasonal',
        'summer_multiplier': 1.5,
        'winter_multiplier': 0.7,
        'expected_mape': 0.20
    },
    'weather_dependent': {
        'correlation': 'temperature',
        'coefficient': 0.6,
        'base_demand': 10,
        'expected_mape': 0.18
    }
}
```

### Acceptance Criteria
- [ ] Prediction MAPE < 20% with 30+ days data
- [ ] Seasonal patterns detected accurately
- [ ] Weather correlation > 0.3 for relevant products
- [ ] Stockout predictions 85% accurate
- [ ] Par level recommendations reduce stockouts by 30%

## 6. Location-Specific Personalization Testing

### Unit Tests (`test_location_personalizer.py`)

```python
class TestLocationPersonalizer(unittest.TestCase):
    
    def setUp(self):
        self.personalizer = LocationPersonalizer(api_key='test')
        
    def test_venue_profile_classification(self):
        """Test venue type classification"""
        venue_type = self.personalizer.classify_venue(
            location='123 Office Park Drive',
            device_metadata=self.office_metadata
        )
        
        self.assertEqual(venue_type, 'office_building')
        
    def test_demographic_product_selection(self):
        """Test product selection based on demographics"""
        recommendations = self.personalizer.recommend_products(
            venue_type='gym',
            demographics={'age_range': '18-35', 'income': 'medium-high'}
        )
        
        # Should recommend protein bars and sports drinks
        product_categories = [r['category'] for r in recommendations]
        self.assertIn('Sports Nutrition', product_categories)
        self.assertIn('Energy Drinks', product_categories)
        
    def test_time_of_day_optimization(self):
        """Test time-based product recommendations"""
        morning_recs = self.personalizer.optimize_by_time(
            base_planogram=self.planogram,
            time_slot='morning'
        )
        
        afternoon_recs = self.personalizer.optimize_by_time(
            base_planogram=self.planogram,
            time_slot='afternoon'
        )
        
        # Morning should prioritize coffee/breakfast
        # Afternoon should prioritize snacks/energy
        self.assertNotEqual(morning_recs[0]['product_id'], 
                          afternoon_recs[0]['product_id'])
```

### Integration Tests (`test_location_personalizer_api.py`)

```python
class TestLocationPersonalizationAPI(unittest.TestCase):
    
    def test_personalize_endpoint(self):
        """Test /api/planogram/personalize endpoint"""
        payload = {
            'device_id': 1,
            'cabinet_index': 0,
            'venue_profile': {
                'type': 'hospital',
                'demographics': {
                    'staff': 200,
                    'visitors': 500,
                    'patients': 100
                }
            }
        }
        
        response = self.app.post('/api/planogram/personalize',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('personalized_planogram', data)
        self.assertIn('relevance_score', data)
        self.assertIn('expected_impact', data)
```

### Test Data Requirements

```python
# test_data/location_data.py
VENUE_PROFILES = {
    'office_building': {
        'peak_hours': [8, 12, 15],
        'preferred_categories': ['Coffee', 'Energy', 'Healthy Snacks'],
        'price_sensitivity': 'low',
        'expected_daily_revenue': 180
    },
    'school': {
        'peak_hours': [10, 12, 15],
        'preferred_categories': ['Sports Drinks', 'Chips', 'Candy'],
        'restrictions': ['energy_drinks', 'alcohol'],
        'price_sensitivity': 'high',
        'expected_daily_revenue': 120
    },
    'gym': {
        'peak_hours': [6, 12, 18],
        'preferred_categories': ['Protein', 'Water', 'Recovery'],
        'price_sensitivity': 'medium',
        'expected_daily_revenue': 150
    }
}
```

### Acceptance Criteria
- [ ] Venue classification 90% accurate
- [ ] Demographic matching improves relevance by 20%
- [ ] Time-based optimization increases peak sales by 15%
- [ ] Revenue increase of $8-12/day per location
- [ ] Personalization respects all restrictions

## 7. Service Route Optimization Testing

### Unit Tests (`test_route_optimizer.py`)

```python
class TestRouteOptimizer(unittest.TestCase):
    
    def setUp(self):
        self.optimizer = ServiceRouteOptimizer(db_path='test.db')
        
    def test_spoilage_prediction(self):
        """Test perishable spoilage risk calculation"""
        risk = self.optimizer.predict_spoilage(
            product_id=11,  # Sandwich (perishable)
            current_stock=5,
            last_service_date='2024-01-01',
            current_date='2024-01-03'
        )
        
        self.assertIn('risk_level', risk)
        self.assertIn('expected_spoilage', risk)
        self.assertIn('recommended_action', risk)
        
        # 2-day old sandwich should show high risk
        self.assertEqual(risk['risk_level'], 'high')
        
    def test_dynamic_reorder_points(self):
        """Test dynamic reorder point calculation"""
        reorder_point = self.optimizer.calculate_reorder_point(
            product_id=1,
            velocity_trend='increasing',
            lead_time_days=2,
            service_level=0.95
        )
        
        self.assertIsInstance(reorder_point, int)
        self.assertGreater(reorder_point, 0)
        
        # Increasing velocity should raise reorder point
        static_point = self.optimizer.calculate_reorder_point(
            product_id=1,
            velocity_trend='stable',
            lead_time_days=2,
            service_level=0.95
        )
        
        self.assertGreater(reorder_point, static_point)
    
    def test_route_consolidation(self):
        """Test route consolidation opportunities"""
        opportunities = self.optimizer.find_consolidation_opportunities(
            routes=self.test_routes,
            constraints={'max_stops': 20, 'max_time': 480}
        )
        
        for opp in opportunities:
            self.assertIn('routes_to_combine', opp)
            self.assertIn('estimated_savings', opp)
            self.assertIn('feasibility_score', opp)
            
            # Savings should be positive
            self.assertGreater(opp['estimated_savings'], 0)
```

### Performance Tests (`test_route_optimizer_performance.py`)

```python
class TestRouteOptimizerPerformance(unittest.TestCase):
    
    def test_large_fleet_optimization(self):
        """Test optimization for large fleet"""
        import time
        
        # Create 100 devices across 10 routes
        devices = self.create_test_fleet(100, 10)
        
        start = time.time()
        optimized_routes = self.optimizer.optimize_all_routes(devices)
        duration = time.time() - start
        
        # Should optimize 100 devices in < 10 seconds
        self.assertLess(duration, 10.0)
        
        # Should reduce total distance
        original_distance = self.calculate_total_distance(devices)
        optimized_distance = self.calculate_total_distance(optimized_routes)
        self.assertLess(optimized_distance, original_distance)
```

### Test Data Requirements

```python
# test_data/route_optimization_data.py
ROUTE_SCENARIOS = {
    'dense_urban': {
        'devices_per_sq_mile': 10,
        'average_distance': 0.5,  # miles
        'service_time': 15,  # minutes
        'expected_consolidation': 0.3
    },
    'suburban': {
        'devices_per_sq_mile': 3,
        'average_distance': 2.0,
        'service_time': 15,
        'expected_consolidation': 0.15
    },
    'mixed_perishable': {
        'perishable_percentage': 0.4,
        'spoilage_window': 3,  # days
        'expected_frequency_increase': 0.5
    }
}
```

### Acceptance Criteria
- [ ] Spoilage predictions 90% accurate
- [ ] Dynamic reorder points reduce stockouts by 25%
- [ ] Route consolidation saves 15% in service costs
- [ ] Labor time predictions within 10% accuracy
- [ ] Overall service cost reduction of 15%

## Performance Testing Framework

### Load Testing (`test_ai_load.py`)

```python
import locust
from locust import HttpUser, task, between

class AIServiceUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def realtime_analysis(self):
        """Test real-time assistant under load"""
        self.client.post('/api/planogram/analyze', json={
            'product_id': 1,
            'slot_position': 'B3',
            'device_id': 1,
            'cabinet_index': 0
        })
    
    @task(2)
    def revenue_prediction(self):
        """Test revenue prediction under load"""
        self.client.post('/api/planogram/predict', json={
            'device_id': 1,
            'cabinet_index': 0,
            'proposed_changes': [{'slot': 'A1', 'product_id': 5}]
        })
    
    @task(1)
    def demand_forecast(self):
        """Test demand forecasting under load"""
        self.client.get('/api/demand/forecast?product_id=1&days=7')
```

### Performance Benchmarks

```python
# test_performance_benchmarks.py
PERFORMANCE_REQUIREMENTS = {
    'realtime_assistant': {
        'p50': 200,  # ms
        'p95': 500,  # ms
        'p99': 800,  # ms
        'throughput': 100  # requests/second
    },
    'revenue_prediction': {
        'p50': 3000,  # ms
        'p95': 7000,  # ms
        'p99': 10000,  # ms
        'throughput': 10  # requests/second
    },
    'demand_forecast': {
        'p50': 1000,  # ms
        'p95': 3000,  # ms
        'p99': 5000,  # ms
        'throughput': 20  # requests/second
    }
}
```

## AI Accuracy Validation

### Accuracy Testing Framework (`test_ai_accuracy.py`)

```python
class TestAIAccuracy(unittest.TestCase):
    
    def setUp(self):
        self.test_set = self.load_test_dataset()
        self.metrics = AccuracyMetrics()
    
    def test_placement_recommendation_accuracy(self):
        """Test accuracy of placement recommendations"""
        correct = 0
        total = 0
        
        for test_case in self.test_set['placements']:
            recommendation = self.assistant.recommend_placement(
                test_case['input']
            )
            
            if recommendation['slot'] == test_case['expected']:
                correct += 1
            total += 1
        
        accuracy = correct / total
        self.assertGreater(accuracy, 0.85, 
                          "Placement accuracy below 85% threshold")
    
    def test_revenue_prediction_accuracy(self):
        """Test revenue prediction accuracy"""
        predictions = []
        actuals = []
        
        for test_case in self.test_set['revenue']:
            prediction = self.predictor.predict(test_case['planogram'])
            predictions.append(prediction['revenue'])
            actuals.append(test_case['actual_revenue'])
        
        mape = self.metrics.calculate_mape(predictions, actuals)
        self.assertLess(mape, 0.15, 
                       "Revenue prediction MAPE exceeds 15%")
    
    def test_confidence_calibration(self):
        """Test that confidence scores are well-calibrated"""
        buckets = {i/10: {'predicted': 0, 'actual': 0} 
                  for i in range(11)}
        
        for test_case in self.test_set['confidence']:
            confidence = test_case['confidence']
            bucket = round(confidence, 1)
            buckets[bucket]['predicted'] += 1
            
            if test_case['correct']:
                buckets[bucket]['actual'] += 1
        
        # Confidence should match accuracy
        for conf_level, counts in buckets.items():
            if counts['predicted'] > 0:
                actual_accuracy = counts['actual'] / counts['predicted']
                self.assertAlmostEqual(actual_accuracy, conf_level, 
                                     delta=0.1)
```

## A/B Testing Framework

### A/B Test Implementation (`ab_testing_framework.py`)

```python
class ABTestingFramework:
    """Framework for A/B testing AI features"""
    
    def __init__(self, db_path='cvd.db'):
        self.db_path = db_path
        self.experiments = {}
    
    def create_experiment(self, name, feature, hypothesis, 
                         sample_size, duration_days):
        """Create new A/B test experiment"""
        experiment = {
            'name': name,
            'feature': feature,
            'hypothesis': hypothesis,
            'sample_size': sample_size,
            'duration_days': duration_days,
            'start_date': datetime.now(),
            'control_group': [],
            'treatment_group': [],
            'metrics': {}
        }
        
        # Randomly assign devices to groups
        devices = self.get_all_devices()
        random.shuffle(devices)
        
        half = len(devices) // 2
        experiment['control_group'] = devices[:half]
        experiment['treatment_group'] = devices[half:]
        
        self.experiments[name] = experiment
        return experiment
    
    def track_metric(self, experiment_name, device_id, metric_name, value):
        """Track metric for experiment"""
        experiment = self.experiments[experiment_name]
        
        if device_id in experiment['control_group']:
            group = 'control'
        elif device_id in experiment['treatment_group']:
            group = 'treatment'
        else:
            return
        
        if metric_name not in experiment['metrics']:
            experiment['metrics'][metric_name] = {
                'control': [],
                'treatment': []
            }
        
        experiment['metrics'][metric_name][group].append(value)
    
    def analyze_results(self, experiment_name, confidence_level=0.95):
        """Analyze A/B test results"""
        from scipy import stats
        
        experiment = self.experiments[experiment_name]
        results = {}
        
        for metric_name, groups in experiment['metrics'].items():
            control = groups['control']
            treatment = groups['treatment']
            
            # Perform t-test
            t_stat, p_value = stats.ttest_ind(treatment, control)
            
            # Calculate effect size
            control_mean = np.mean(control)
            treatment_mean = np.mean(treatment)
            effect_size = (treatment_mean - control_mean) / control_mean
            
            results[metric_name] = {
                'control_mean': control_mean,
                'treatment_mean': treatment_mean,
                'effect_size': effect_size,
                'p_value': p_value,
                'significant': p_value < (1 - confidence_level),
                'confidence_interval': stats.t.interval(
                    confidence_level, 
                    len(treatment) - 1,
                    treatment_mean,
                    stats.sem(treatment)
                )
            }
        
        return results
```

### A/B Test Scenarios (`test_ab_scenarios.py`)

```python
class TestABScenarios(unittest.TestCase):
    
    def setUp(self):
        self.ab_framework = ABTestingFramework()
    
    def test_realtime_assistant_impact(self):
        """Test impact of real-time assistant on revenue"""
        experiment = self.ab_framework.create_experiment(
            name='realtime_assistant_v1',
            feature='realtime_placement_scoring',
            hypothesis='Real-time AI feedback increases revenue by 10%',
            sample_size=50,
            duration_days=30
        )
        
        # Simulate 30 days of data
        self.simulate_experiment_data(experiment)
        
        # Analyze results
        results = self.ab_framework.analyze_results('realtime_assistant_v1')
        
        # Verify hypothesis
        revenue_impact = results['daily_revenue']['effect_size']
        self.assertGreater(revenue_impact, 0.10)
        self.assertTrue(results['daily_revenue']['significant'])
    
    def test_prediction_accuracy_over_time(self):
        """Test if predictions improve with more data"""
        experiment = self.ab_framework.create_experiment(
            name='prediction_learning',
            feature='revenue_prediction',
            hypothesis='Prediction accuracy improves 5% per month',
            sample_size=30,
            duration_days=90
        )
        
        # Track accuracy over time
        for day in range(90):
            for device_id in experiment['treatment_group']:
                accuracy = self.measure_prediction_accuracy(device_id, day)
                self.ab_framework.track_metric(
                    'prediction_learning',
                    device_id,
                    'prediction_accuracy',
                    accuracy
                )
        
        # Verify improvement
        results = self.ab_framework.analyze_results('prediction_learning')
        
        # Compare first month to third month
        first_month = results['prediction_accuracy']['treatment'][:30]
        third_month = results['prediction_accuracy']['treatment'][60:]
        
        improvement = (np.mean(third_month) - np.mean(first_month)) / np.mean(first_month)
        self.assertGreater(improvement, 0.10)  # 10% improvement over 3 months
```

## Regression Test Suite

### Regression Test Organization (`test_regression_suite.py`)

```python
class RegressionTestSuite(unittest.TestSuite):
    """Comprehensive regression test suite for AI features"""
    
    def __init__(self):
        super().__init__()
        
        # Core functionality tests
        self.addTest(TestPlanogramOptimizer('test_get_sales_data'))
        self.addTest(TestPlanogramOptimizer('test_calculate_performance_metrics'))
        
        # AI service tests
        self.addTest(TestRealtimeAssistant('test_placement_scoring_valid_placement'))
        self.addTest(TestRevenuePrediction('test_baseline_calculation'))
        self.addTest(TestHeatZoneAnalysis('test_zone_value_calculation'))
        self.addTest(TestAffinityEngine('test_affinity_matrix_calculation'))
        self.addTest(TestDemandForecaster('test_seasonal_pattern_detection'))
        self.addTest(TestLocationPersonalizer('test_venue_profile_classification'))
        self.addTest(TestRouteOptimizer('test_spoilage_prediction'))
        
        # Integration tests
        self.addTest(TestRealtimeAssistantAPI('test_analyze_placement_endpoint'))
        self.addTest(TestRevenuePredictionAPI('test_predict_endpoint'))
        
        # Performance tests
        self.addTest(TestDemandForecasterPerformance('test_bulk_prediction_performance'))
        self.addTest(TestRouteOptimizerPerformance('test_large_fleet_optimization'))
    
    def run_with_coverage(self):
        """Run suite with coverage reporting"""
        import coverage
        
        cov = coverage.Coverage()
        cov.start()
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(self)
        
        cov.stop()
        cov.save()
        
        # Generate coverage report
        print("\nCoverage Report:")
        cov.report(include=['ai_services/*.py', 'planogram_optimizer.py'])
        
        return result
```

### Continuous Integration Configuration (`.github/workflows/ai_tests.yml`)

```yaml
name: AI Feature Tests

on:
  push:
    paths:
      - 'ai_services/**'
      - 'planogram_optimizer.py'
      - 'tests/test_*.py'
  pull_request:
    paths:
      - 'ai_services/**'
      - 'planogram_optimizer.py'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov locust
    
    - name: Run unit tests
      run: |
        pytest tests/test_realtime_assistant.py -v
        pytest tests/test_revenue_predictor.py -v
        pytest tests/test_heat_zone_analysis.py -v
        pytest tests/test_affinity_engine.py -v
        pytest tests/test_demand_forecaster.py -v
        pytest tests/test_location_personalizer.py -v
        pytest tests/test_route_optimizer.py -v
    
    - name: Run integration tests
      run: |
        pytest tests/test_*_api.py -v
    
    - name: Run performance tests
      run: |
        pytest tests/test_*_performance.py -v
    
    - name: Check AI accuracy
      run: |
        python tests/test_ai_accuracy.py
    
    - name: Generate coverage report
      run: |
        pytest --cov=ai_services --cov=planogram_optimizer tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Test Execution Plan

### Phase 1: Quick Wins Testing (Week 1)
1. **Day 1-2**: Set up test environment and data
2. **Day 3-4**: Unit tests for enhanced optimizer
3. **Day 5**: Integration tests for existing endpoints

### Phase 2: Core Enhancement Testing (Weeks 2-3)
1. **Week 2**: Real-time assistant and revenue predictor tests
2. **Week 3**: Heat zone and affinity engine tests

### Phase 3: Advanced Testing (Weeks 4-5)
1. **Week 4**: Demand forecasting and personalization tests
2. **Week 5**: Route optimization and performance tests

### Phase 4: Validation & Optimization (Week 6)
1. **Day 1-2**: A/B test framework setup
2. **Day 3-4**: Accuracy validation tests
3. **Day 5**: Regression suite finalization

## Test Metrics & Reporting

### Key Metrics to Track
1. **Test Coverage**: Target > 90% for AI services
2. **Test Execution Time**: < 10 minutes for full suite
3. **Failure Rate**: < 5% for stable tests
4. **Performance Benchmarks**: Meet all defined thresholds
5. **AI Accuracy**: Meet all accuracy requirements

### Reporting Dashboard

```python
class TestMetricsDashboard:
    """Generate test metrics dashboard"""
    
    def generate_report(self):
        return {
            'coverage': {
                'ai_services': 92.5,
                'api_endpoints': 88.3,
                'overall': 90.4
            },
            'performance': {
                'realtime_assistant': {'p95': 450, 'target': 500},
                'revenue_prediction': {'p95': 6500, 'target': 7000},
                'demand_forecast': {'p95': 2800, 'target': 3000}
            },
            'ai_accuracy': {
                'placement_recommendations': 0.87,
                'revenue_predictions': 0.85,
                'demand_forecasts': 0.82
            },
            'test_health': {
                'total_tests': 247,
                'passing': 235,
                'failing': 12,
                'skipped': 0
            }
        }
```

## Risk Mitigation Testing

### Critical Path Tests
1. **API Failure Handling**: Test fallback mechanisms
2. **Data Quality Issues**: Test with missing/corrupt data
3. **Performance Degradation**: Test under heavy load
4. **Model Drift**: Test with changing patterns

### Security Testing
1. **Input Validation**: Test SQL injection prevention
2. **API Authentication**: Test unauthorized access
3. **Data Privacy**: Test PII handling
4. **Rate Limiting**: Test API abuse prevention

## Conclusion

This comprehensive testing strategy ensures the AI planogram enhancement system meets all quality, performance, and accuracy requirements. The multi-layered approach with unit, integration, E2E, and performance testing provides confidence in the system's reliability and effectiveness. Regular execution of the regression suite and continuous monitoring through A/B testing ensures long-term system health and improvement validation.