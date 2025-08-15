"""
Context-Aware Recommendation System for Planograms
Provides location-specific, time-aware, and demographic-based recommendations
"""

import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import anthropic
import numpy as np

class ContextAwareRecommender:
    """Generate context-specific planogram recommendations"""
    
    def __init__(self, api_key: str, db_path: str = 'cvd.db'):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.db_path = db_path
        self.context_cache = {}
        
    def generate_contextual_recommendations(self, device_id: int, 
                                          cabinet_index: int) -> Dict:
        """
        Generate recommendations based on multiple context factors
        """
        
        # Gather all context data
        location_context = self._get_location_context(device_id)
        temporal_context = self._get_temporal_context()
        demographic_context = self._get_demographic_context(location_context)
        weather_context = self._get_weather_context(location_context)
        event_context = self._get_event_context(location_context)
        competitive_context = self._get_competitive_context(device_id)
        
        # Structure context for AI
        full_context = self._structure_context(
            location_context,
            temporal_context,
            demographic_context,
            weather_context,
            event_context,
            competitive_context
        )
        
        # Generate AI recommendations
        recommendations = self._generate_ai_recommendations(full_context, device_id, cabinet_index)
        
        # Apply seasonal adjustments
        seasonal_recommendations = self._apply_seasonal_adjustments(
            recommendations, temporal_context
        )
        
        # Generate location-specific strategies
        location_strategies = self._generate_location_strategies(
            location_context, demographic_context
        )
        
        return {
            'context_analysis': full_context,
            'recommendations': seasonal_recommendations,
            'location_strategies': location_strategies,
            'implementation_timeline': self._create_timeline(seasonal_recommendations),
            'monitoring_metrics': self._define_metrics(full_context)
        }
    
    def _get_location_context(self, device_id: int) -> Dict:
        """Get location-specific context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            d.location_id,
            l.name,
            l.address,
            l.location_type,
            l.foot_traffic,
            l.operating_hours,
            COUNT(DISTINCT d2.id) as nearby_devices
        FROM devices d
        JOIN locations l ON d.location_id = l.id
        LEFT JOIN devices d2 ON d2.location_id = d.location_id AND d2.id != d.id
        WHERE d.id = ?
        GROUP BY d.location_id
        """
        cursor.execute(query, (device_id,))
        result = cursor.fetchone()
        
        # Get location performance history
        perf_query = """
        SELECT 
            AVG(s.sale_cash) as avg_daily_revenue,
            COUNT(DISTINCT DATE(s.created_at)) as active_days,
            COUNT(DISTINCT s.product_id) as product_variety_sold
        FROM sales s
        JOIN devices d ON s.device_id = d.id
        WHERE d.location_id = ? AND s.created_at > datetime('now', '-90 days')
        """
        
        location_id = result[0] if result else None
        if location_id:
            cursor.execute(perf_query, (location_id,))
            perf = cursor.fetchone()
        else:
            perf = (0, 0, 0)
        
        conn.close()
        
        if result:
            return {
                'location_id': result[0],
                'name': result[1],
                'address': result[2],
                'type': result[3] or 'Unknown',
                'foot_traffic': result[4] or 'Medium',
                'operating_hours': result[5] or '24/7',
                'nearby_devices': result[6],
                'performance': {
                    'avg_daily_revenue': perf[0] or 0,
                    'active_days': perf[1] or 0,
                    'product_variety': perf[2] or 0
                },
                'characteristics': self._infer_location_characteristics(result[3])
            }
        
        return {
            'type': 'Unknown',
            'characteristics': {},
            'performance': {}
        }
    
    def _get_temporal_context(self) -> Dict:
        """Get time-based context"""
        now = datetime.now()
        
        # Determine season
        month = now.month
        if month in [12, 1, 2]:
            season = 'Winter'
        elif month in [3, 4, 5]:
            season = 'Spring'
        elif month in [6, 7, 8]:
            season = 'Summer'
        else:
            season = 'Fall'
        
        # Holiday detection
        holidays = self._detect_upcoming_holidays(now)
        
        return {
            'current_date': now.isoformat(),
            'day_of_week': now.strftime('%A'),
            'week_of_month': (now.day - 1) // 7 + 1,
            'month': now.strftime('%B'),
            'season': season,
            'quarter': f'Q{(month - 1) // 3 + 1}',
            'upcoming_holidays': holidays,
            'is_weekend': now.weekday() >= 5,
            'time_patterns': {
                'morning_rush': '6:00-9:00',
                'lunch_peak': '11:30-13:30',
                'afternoon_break': '14:30-16:00',
                'evening_rush': '17:00-19:00'
            }
        }
    
    def _get_demographic_context(self, location_context: Dict) -> Dict:
        """Infer demographic context from location type"""
        location_type = location_context.get('type', 'Unknown')
        
        demographics = {
            'Office': {
                'primary_age': '25-55',
                'income_level': 'Medium-High',
                'preferences': ['Coffee', 'Healthy snacks', 'Quick meals'],
                'peak_times': ['Morning', 'Lunch', 'Afternoon'],
                'price_sensitivity': 'Low'
            },
            'School': {
                'primary_age': '18-25',
                'income_level': 'Low',
                'preferences': ['Energy drinks', 'Snacks', 'Value items'],
                'peak_times': ['Between classes', 'Late night'],
                'price_sensitivity': 'High'
            },
            'Hospital': {
                'primary_age': 'Mixed',
                'income_level': 'Mixed',
                'preferences': ['Coffee', 'Comfort food', 'Healthy options'],
                'peak_times': ['24/7', 'Visitor hours'],
                'price_sensitivity': 'Medium'
            },
            'Gym': {
                'primary_age': '20-45',
                'income_level': 'Medium',
                'preferences': ['Protein bars', 'Sports drinks', 'Water'],
                'peak_times': ['Early morning', 'Evening'],
                'price_sensitivity': 'Low'
            },
            'Transit': {
                'primary_age': 'Mixed',
                'income_level': 'Mixed',
                'preferences': ['Quick snacks', 'Beverages', 'Travel items'],
                'peak_times': ['Rush hours', 'Weekends'],
                'price_sensitivity': 'Medium'
            }
        }
        
        return demographics.get(location_type, {
            'primary_age': 'Mixed',
            'income_level': 'Mixed',
            'preferences': ['General items'],
            'peak_times': ['Business hours'],
            'price_sensitivity': 'Medium'
        })
    
    def _get_weather_context(self, location_context: Dict) -> Dict:
        """Get weather context (simulated for now)"""
        # In production, would integrate with weather API
        current_month = datetime.now().month
        
        if current_month in [12, 1, 2]:
            return {
                'temperature': 'Cold',
                'conditions': 'Winter',
                'recommendations': ['Hot beverages', 'Comfort food', 'Soup']
            }
        elif current_month in [6, 7, 8]:
            return {
                'temperature': 'Hot',
                'conditions': 'Summer',
                'recommendations': ['Cold beverages', 'Ice cream', 'Light snacks']
            }
        else:
            return {
                'temperature': 'Mild',
                'conditions': 'Moderate',
                'recommendations': ['Standard mix']
            }
    
    def _get_event_context(self, location_context: Dict) -> Dict:
        """Detect local events that might affect sales"""
        # Simulated event detection
        events = []
        
        location_type = location_context.get('type', '')
        
        if location_type == 'School':
            # Check for academic calendar events
            month = datetime.now().month
            if month == 9:
                events.append({'name': 'Back to School', 'impact': 'High', 'duration': '2 weeks'})
            elif month in [5, 6]:
                events.append({'name': 'Finals Week', 'impact': 'High', 'duration': '1 week'})
        
        elif location_type == 'Office':
            # Check for business events
            if datetime.now().day <= 5:
                events.append({'name': 'Month End', 'impact': 'Medium', 'duration': '3 days'})
        
        return {
            'upcoming_events': events,
            'event_impact': 'High' if events else 'None'
        }
    
    def _get_competitive_context(self, device_id: int) -> Dict:
        """Analyze competitive landscape"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get devices at same location
        query = """
        SELECT COUNT(*) as competitor_count
        FROM devices d1
        JOIN devices d2 ON d1.location_id = d2.location_id
        WHERE d1.id = ? AND d2.id != d1.id
        """
        cursor.execute(query, (device_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        competitor_count = result[0] if result else 0
        
        return {
            'competitor_count': competitor_count,
            'competition_level': 'High' if competitor_count > 2 else 'Low',
            'differentiation_needed': competitor_count > 0,
            'strategies': self._get_competitive_strategies(competitor_count)
        }
    
    def _structure_context(self, location: Dict, temporal: Dict, 
                          demographic: Dict, weather: Dict, 
                          event: Dict, competitive: Dict) -> Dict:
        """Structure all context for AI processing"""
        
        return {
            'location': {
                'type': location.get('type'),
                'traffic': location.get('foot_traffic'),
                'hours': location.get('operating_hours'),
                'performance': location.get('performance', {})
            },
            'temporal': {
                'season': temporal['season'],
                'day_type': 'Weekend' if temporal['is_weekend'] else 'Weekday',
                'holidays': temporal['upcoming_holidays'],
                'month': temporal['month']
            },
            'demographic': {
                'age_group': demographic.get('primary_age'),
                'income': demographic.get('income_level'),
                'preferences': demographic.get('preferences', []),
                'price_sensitivity': demographic.get('price_sensitivity')
            },
            'weather': weather,
            'events': event['upcoming_events'],
            'competition': {
                'level': competitive['competition_level'],
                'differentiation': competitive['differentiation_needed']
            }
        }
    
    def _generate_ai_recommendations(self, context: Dict, device_id: int, 
                                    cabinet_index: int) -> List[Dict]:
        """Generate AI recommendations based on context"""
        
        prompt = f"""<context>
Location: {context['location']['type']} - {context['location']['traffic']} traffic
Hours: {context['location']['hours']}
Performance: ${context['location']['performance'].get('avg_daily_revenue', 0):.2f}/day

Time: {context['temporal']['season']} - {context['temporal']['day_type']}
Month: {context['temporal']['month']}
Holidays: {context['temporal']['holidays']}

Demographics:
- Age: {context['demographic']['age_group']}
- Income: {context['demographic']['income']}
- Preferences: {', '.join(context['demographic']['preferences'])}
- Price Sensitivity: {context['demographic']['price_sensitivity']}

Weather: {context['weather']['temperature']} - {context['weather']['conditions']}
Events: {len(context['events'])} upcoming events
Competition: {context['competition']['level']}
</context>

Generate specific, contextual planogram recommendations that:
1. Match the demographic preferences
2. Align with seasonal/weather conditions
3. Consider upcoming events and holidays
4. Account for competition level
5. Optimize for location type and traffic patterns

Provide 5-8 specific product recommendations with:
- Product name and category
- Recommended slot position (A1, B2, etc.)
- Context-based reasoning
- Expected sales impact
- Priority level (1-5)

Format as JSON array of recommendations."""
        
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                temperature=0.6,
                system="You are a retail merchandising expert specializing in location-specific optimization.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                return recommendations
                
        except Exception as e:
            print(f"AI recommendation error: {e}")
        
        # Fallback recommendations
        return self._generate_fallback_recommendations(context)
    
    def _generate_fallback_recommendations(self, context: Dict) -> List[Dict]:
        """Generate rule-based fallback recommendations"""
        recommendations = []
        
        # Season-based
        if context['temporal']['season'] == 'Summer':
            recommendations.append({
                'product': 'Sports Drink',
                'category': 'Beverage',
                'slot': 'B2',
                'reasoning': 'High demand in summer heat',
                'impact': '+15% sales',
                'priority': 1
            })
        elif context['temporal']['season'] == 'Winter':
            recommendations.append({
                'product': 'Hot Chocolate',
                'category': 'Beverage',
                'slot': 'A1',
                'reasoning': 'Popular winter beverage',
                'impact': '+10% sales',
                'priority': 1
            })
        
        # Demographics-based
        if 'Healthy' in str(context['demographic']['preferences']):
            recommendations.append({
                'product': 'Protein Bar',
                'category': 'Snack',
                'slot': 'C3',
                'reasoning': 'Matches health-conscious demographic',
                'impact': '+8% sales',
                'priority': 2
            })
        
        return recommendations
    
    def _apply_seasonal_adjustments(self, recommendations: List[Dict], 
                                   temporal_context: Dict) -> List[Dict]:
        """Apply seasonal adjustments to recommendations"""
        
        season = temporal_context['season']
        month = datetime.now().month
        
        # Seasonal product mappings
        seasonal_products = {
            'Summer': {
                'add': ['Ice Cream', 'Iced Coffee', 'Sports Drink', 'Salad'],
                'remove': ['Hot Chocolate', 'Soup', 'Hot Coffee'],
                'boost': ['Water', 'Juice', 'Light Snacks']
            },
            'Winter': {
                'add': ['Hot Chocolate', 'Soup', 'Coffee', 'Tea'],
                'remove': ['Ice Cream', 'Iced Coffee', 'Cold Salad'],
                'boost': ['Comfort Food', 'Hot Beverages']
            },
            'Spring': {
                'add': ['Fresh Fruit', 'Salad', 'Smoothie'],
                'remove': ['Heavy Meals'],
                'boost': ['Healthy Options']
            },
            'Fall': {
                'add': ['Pumpkin Items', 'Warm Beverages', 'Seasonal Snacks'],
                'remove': ['Summer Items'],
                'boost': ['Comfort Food']
            }
        }
        
        adjustments = seasonal_products.get(season, {})
        
        # Modify recommendations based on season
        adjusted = []
        for rec in recommendations:
            rec_copy = rec.copy()
            
            # Boost priority for seasonal items
            if any(item in rec.get('product', '') for item in adjustments.get('boost', [])):
                rec_copy['priority'] = max(1, rec_copy.get('priority', 3) - 1)
                rec_copy['seasonal_boost'] = True
            
            # Flag items to remove
            if any(item in rec.get('product', '') for item in adjustments.get('remove', [])):
                rec_copy['seasonal_warning'] = 'Consider removing - out of season'
                rec_copy['priority'] = min(5, rec_copy.get('priority', 3) + 2)
            
            adjusted.append(rec_copy)
        
        # Add seasonal must-haves
        for product in adjustments.get('add', [])[:2]:  # Top 2 seasonal adds
            adjusted.insert(0, {
                'product': product,
                'category': 'Seasonal',
                'slot': 'A1',  # Premium position
                'reasoning': f'High demand in {season}',
                'impact': '+12% sales',
                'priority': 1,
                'seasonal': True
            })
        
        return adjusted
    
    def _generate_location_strategies(self, location: Dict, demographic: Dict) -> List[Dict]:
        """Generate location-specific optimization strategies"""
        strategies = []
        
        location_type = location.get('type', 'Unknown')
        
        # Office location strategies
        if location_type == 'Office':
            strategies.append({
                'name': 'Morning Rush Optimization',
                'description': 'Stock coffee and breakfast items in premium positions',
                'timing': '6:00 AM - 10:00 AM',
                'products': ['Coffee', 'Energy Bars', 'Breakfast Sandwiches'],
                'expected_impact': '+20% morning sales'
            })
            strategies.append({
                'name': 'Afternoon Energy Boost',
                'description': 'Feature energy drinks and snacks at eye level',
                'timing': '2:00 PM - 4:00 PM',
                'products': ['Energy Drinks', 'Candy', 'Chips'],
                'expected_impact': '+15% afternoon sales'
            })
        
        # School location strategies
        elif location_type == 'School':
            strategies.append({
                'name': 'Study Session Support',
                'description': 'Stock brain food and energy items',
                'timing': 'Library hours and late night',
                'products': ['Energy Drinks', 'Trail Mix', 'Protein Bars'],
                'expected_impact': '+25% during exam periods'
            })
            strategies.append({
                'name': 'Value Pack Focus',
                'description': 'Emphasize budget-friendly options',
                'timing': 'All day',
                'products': ['Value snacks', 'Bundle deals'],
                'expected_impact': '+30% unit sales'
            })
        
        # Hospital location strategies
        elif location_type == 'Hospital':
            strategies.append({
                'name': '24/7 Availability',
                'description': 'Ensure round-the-clock essentials',
                'timing': 'Night shift emphasis',
                'products': ['Coffee', 'Sandwiches', 'Comfort snacks'],
                'expected_impact': '+40% overnight sales'
            })
        
        # Gym location strategies
        elif location_type == 'Gym':
            strategies.append({
                'name': 'Post-Workout Recovery',
                'description': 'Feature protein and recovery products prominently',
                'timing': 'Peak gym hours',
                'products': ['Protein shakes', 'Recovery drinks', 'Protein bars'],
                'expected_impact': '+35% sales to gym members'
            })
        
        return strategies
    
    def _create_timeline(self, recommendations: List[Dict]) -> Dict:
        """Create implementation timeline for recommendations"""
        
        # Sort by priority
        sorted_recs = sorted(recommendations, key=lambda x: x.get('priority', 5))
        
        timeline = {
            'immediate': {
                'timeframe': 'Next service visit',
                'items': [r for r in sorted_recs if r.get('priority', 5) <= 2],
                'expected_impact': 'Quick wins - 10-15% revenue boost'
            },
            'short_term': {
                'timeframe': 'Next 2 weeks',
                'items': [r for r in sorted_recs if 3 <= r.get('priority', 5) <= 4],
                'expected_impact': 'Optimization - 5-10% improvement'
            },
            'long_term': {
                'timeframe': 'Next month',
                'items': [r for r in sorted_recs if r.get('priority', 5) >= 5],
                'expected_impact': 'Strategic changes - sustained growth'
            }
        }
        
        return timeline
    
    def _define_metrics(self, context: Dict) -> Dict:
        """Define success metrics based on context"""
        
        metrics = {
            'primary': [],
            'secondary': [],
            'monitoring_frequency': 'Daily'
        }
        
        # Revenue is always primary
        metrics['primary'].append({
            'name': 'Daily Revenue',
            'target': '+15%',
            'measurement': 'Compare to 30-day average'
        })
        
        # Context-specific metrics
        if context['demographic']['price_sensitivity'] == 'High':
            metrics['primary'].append({
                'name': 'Unit Sales',
                'target': '+20%',
                'measurement': 'Daily unit count'
            })
        
        if context['competition']['level'] == 'High':
            metrics['primary'].append({
                'name': 'Market Share',
                'target': 'Maintain or grow',
                'measurement': 'Sales vs nearby machines'
            })
        
        # Seasonal metrics
        if context['temporal']['season'] in ['Summer', 'Winter']:
            metrics['secondary'].append({
                'name': 'Seasonal Product Performance',
                'target': '25% of sales',
                'measurement': 'Seasonal category sales'
            })
        
        # Event metrics
        if context['events']:
            metrics['secondary'].append({
                'name': 'Event Sales Spike',
                'target': '+30% during events',
                'measurement': 'Sales during event periods'
            })
        
        return metrics
    
    def _infer_location_characteristics(self, location_type: str) -> Dict:
        """Infer characteristics from location type"""
        
        characteristics = {
            'Office': {
                'customer_type': 'Professional',
                'dwell_time': 'Short',
                'purchase_frequency': 'Daily',
                'basket_size': 'Small',
                'peak_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            },
            'School': {
                'customer_type': 'Student',
                'dwell_time': 'Variable',
                'purchase_frequency': 'Multiple daily',
                'basket_size': 'Small',
                'peak_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
            },
            'Hospital': {
                'customer_type': 'Mixed',
                'dwell_time': 'Long',
                'purchase_frequency': 'Sporadic',
                'basket_size': 'Medium',
                'peak_days': ['All days']
            },
            'Gym': {
                'customer_type': 'Fitness-focused',
                'dwell_time': 'Medium',
                'purchase_frequency': 'Post-workout',
                'basket_size': 'Small',
                'peak_days': ['Monday', 'Wednesday', 'Saturday']
            }
        }
        
        return characteristics.get(location_type, {
            'customer_type': 'General',
            'dwell_time': 'Medium',
            'purchase_frequency': 'Variable',
            'basket_size': 'Medium',
            'peak_days': ['All days']
        })
    
    def _detect_upcoming_holidays(self, current_date: datetime) -> List[str]:
        """Detect upcoming holidays within 30 days"""
        holidays = []
        
        # Simple holiday detection (would use proper calendar API in production)
        month = current_date.month
        day = current_date.day
        
        holiday_calendar = {
            1: [(1, "New Year's Day"), (15, "MLK Day")],
            2: [(14, "Valentine's Day"), (20, "Presidents Day")],
            3: [(17, "St. Patrick's Day")],
            4: [(1, "April Fools"), (22, "Earth Day")],
            5: [(5, "Cinco de Mayo"), (29, "Memorial Day")],
            6: [(19, "Juneteenth")],
            7: [(4, "Independence Day")],
            9: [(4, "Labor Day")],
            10: [(31, "Halloween")],
            11: [(11, "Veterans Day"), (23, "Thanksgiving")],
            12: [(25, "Christmas"), (31, "New Year's Eve")]
        }
        
        current_holidays = holiday_calendar.get(month, [])
        for holiday_day, holiday_name in current_holidays:
            if holiday_day >= day and holiday_day <= day + 30:
                holidays.append(holiday_name)
        
        # Check next month too
        next_month = (month % 12) + 1
        days_in_current = 30 - day
        if days_in_current > 0:
            next_holidays = holiday_calendar.get(next_month, [])
            for holiday_day, holiday_name in next_holidays:
                if holiday_day <= days_in_current:
                    holidays.append(holiday_name)
        
        return holidays
    
    def _get_competitive_strategies(self, competitor_count: int) -> List[str]:
        """Generate competitive strategies based on competition level"""
        
        if competitor_count == 0:
            return ["Maintain standard pricing", "Focus on variety"]
        elif competitor_count <= 2:
            return ["Differentiate with unique products", "Competitive pricing on staples"]
        else:
            return ["Aggressive pricing", "Exclusive products", "Superior freshness"]