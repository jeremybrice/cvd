"""
Advanced Prompt Templates for Complex AI Planogram Scenarios
Production-ready templates with chain-of-thought reasoning
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# =============================================================================
# ADVANCED PROMPT PATTERNS
# =============================================================================

class ReasoningPattern(Enum):
    """Different reasoning patterns for complex analysis"""
    CHAIN_OF_THOUGHT = "cot"
    TREE_OF_THOUGHT = "tot"
    SELF_CONSISTENCY = "sc"
    LEAST_TO_MOST = "ltm"
    STEP_BY_STEP = "sbs"

class AdvancedPromptTemplates:
    """Advanced prompt engineering patterns for complex scenarios"""
    
    @staticmethod
    def multi_objective_optimization() -> str:
        """Template for balancing multiple competing objectives"""
        return """<role>
You are a multi-objective optimization expert for vending machine planograms.
</role>

<objectives>
1. Revenue Maximization (weight: {revenue_weight})
2. Customer Satisfaction (weight: {satisfaction_weight})
3. Inventory Turnover (weight: {turnover_weight})
4. Product Variety (weight: {variety_weight})
5. Operational Efficiency (weight: {efficiency_weight})
</objectives>

<current_state>
{current_planogram_analysis}
</current_state>

<constraints>
Physical: {physical_constraints}
Business: {business_rules}
Regulatory: {compliance_requirements}
</constraints>

<chain_of_thought>
Let me analyze this step-by-step:

Step 1: Evaluate current performance against each objective
- Revenue: Current daily revenue is ${current_revenue}
- Satisfaction: Current NPS score is {nps_score}
- Turnover: Average days inventory is {avg_inventory_days}
- Variety: {unique_products} unique products across {categories} categories
- Efficiency: Service time averages {service_minutes} minutes

Step 2: Identify conflicts between objectives
- High revenue products may reduce variety
- Fast turnover may conflict with customer favorites
- Operational efficiency may limit assortment complexity

Step 3: Find Pareto-optimal solutions
- Solutions where improving one objective worsens another
- Look for win-win opportunities first

Step 4: Apply weighted scoring
- Calculate composite score for each configuration
- Rank alternatives by total weighted score

Step 5: Recommend balanced solution
</chain_of_thought>

<analysis_framework>
For each potential configuration, calculate:
1. Revenue Impact = (predicted_revenue - current_revenue) / current_revenue
2. Satisfaction Impact = estimated_nps_change / 100
3. Turnover Impact = (1 / new_avg_days) - (1 / current_avg_days)
4. Variety Impact = (new_unique_count - current_unique_count) / current_unique_count
5. Efficiency Impact = (current_service_time - new_service_time) / current_service_time

Composite Score = Σ(objective_weight × objective_impact)
</analysis_framework>

<output_format>
{{
    "pareto_frontier": [
        {{
            "configuration_id": "string",
            "scores": {{
                "revenue": float,
                "satisfaction": float,
                "turnover": float,
                "variety": float,
                "efficiency": float,
                "composite": float
            }},
            "changes": [
                {{
                    "slot": "position",
                    "from_product": "name",
                    "to_product": "name",
                    "impact": "description"
                }}
            ],
            "tradeoffs": [
                {{
                    "gain": "what_improves",
                    "loss": "what_worsens",
                    "magnitude": "small|medium|large"
                }}
            ]
        }}
    ],
    "recommended_solution": {{
        "configuration_id": "string",
        "reasoning": "why_this_balances_objectives",
        "implementation_steps": ["ordered_list"],
        "expected_outcomes": {{
            "30_days": {{}},
            "60_days": {{}},
            "90_days": {{}}
        }},
        "risk_mitigation": [
            {{
                "risk": "description",
                "mitigation": "strategy"
            }}
        ]
    }},
    "sensitivity_analysis": {{
        "most_sensitive_to": "objective_name",
        "robust_choices": ["products_that_work_across_scenarios"],
        "avoid": ["high_risk_changes"]
    }}
}}
</output_format>"""

    @staticmethod
    def anomaly_detection_and_diagnosis() -> str:
        """Template for detecting and diagnosing performance anomalies"""
        return """<role>
You are a diagnostic expert identifying and explaining vending machine performance anomalies.
</role>

<performance_data>
{time_series_metrics}
</performance_data>

<expected_patterns>
Historical baselines: {historical_baselines}
Seasonal patterns: {seasonal_patterns}
Day-of-week effects: {dow_patterns}
</expected_patterns>

<anomaly_detection_framework>
1. Statistical Outliers
   - Check if metrics fall outside 2σ bounds
   - Use IQR method for robust outlier detection
   - Apply ARIMA residual analysis

2. Pattern Breaks
   - Sudden level shifts
   - Trend reversals
   - Seasonality disruptions

3. Correlation Anomalies
   - Products that usually sell together
   - Time-based purchase patterns
   - Price-volume relationships

4. Contextual Anomalies
   - Performance vs similar locations
   - Performance vs same venue type
   - Performance vs weather/events
</anomaly_detection_framework>

<root_cause_analysis>
For each detected anomaly, investigate:

1. Internal Factors
   - Stockouts: {stockout_data}
   - Planogram changes: {recent_changes}
   - Pricing adjustments: {price_history}
   - Machine malfunctions: {service_logs}

2. External Factors
   - Weather: {weather_data}
   - Local events: {event_calendar}
   - Competitor actions: {competitive_intel}
   - Seasonal shifts: {seasonal_context}

3. Product-Specific Issues
   - Expiration/freshness: {product_dates}
   - Quality complaints: {feedback_data}
   - Substitution effects: {cross_elasticity}

4. Location Factors
   - Foot traffic changes: {traffic_data}
   - Construction/obstacles: {location_notes}
   - Operating hour changes: {schedule_changes}
</root_cause_analysis>

<diagnostic_reasoning>
Apply systematic diagnosis:

Step 1: Isolate the anomaly
- When did it start? {anomaly_start_time}
- Which products affected? {affected_products}
- What's the magnitude? {deviation_percentage}

Step 2: Check for correlations
- Other metrics affected? {correlated_metrics}
- Similar issues elsewhere? {network_comparison}
- Pattern or one-time? {frequency_analysis}

Step 3: Test hypotheses
- Most likely cause based on evidence
- Alternative explanations
- Required data to confirm

Step 4: Recommend remediation
- Immediate actions
- Preventive measures
- Monitoring plan
</diagnostic_reasoning>

<output_format>
{{
    "anomalies_detected": [
        {{
            "metric": "name",
            "timestamp": "when_detected",
            "severity": "high|medium|low",
            "deviation": {{
                "expected": float,
                "actual": float,
                "sigma": float
            }},
            "classification": "outlier|trend_break|correlation|contextual"
        }}
    ],
    "root_cause_analysis": [
        {{
            "anomaly_id": "reference",
            "most_likely_cause": {{
                "category": "internal|external|product|location",
                "specific_cause": "description",
                "confidence": float,
                "evidence": ["supporting_facts"]
            }},
            "alternative_causes": [
                {{
                    "cause": "description",
                    "probability": float
                }}
            ],
            "data_needed": ["what_would_confirm_diagnosis"]
        }}
    ],
    "recommendations": [
        {{
            "priority": "immediate|high|medium|low",
            "action": "specific_action",
            "expected_impact": "description",
            "effort": "minutes|hours|days",
            "owner": "role_responsible"
        }}
    ],
    "preventive_measures": [
        {{
            "measure": "description",
            "implementation": "how_to",
            "monitoring": "what_to_track"
        }}
    ],
    "forecast_adjustment": {{
        "original_forecast": float,
        "adjusted_forecast": float,
        "adjustment_reason": "string",
        "confidence_interval": [lower, upper]
    }}
}}
</output_format>"""

    @staticmethod
    def competitive_intelligence_analysis() -> str:
        """Template for analyzing competitive landscape and positioning"""
        return """<role>
You are a competitive intelligence analyst for vending machine operations.
</role>

<market_context>
Location: {location_details}
Venue type: {venue_type}
Our machine: {our_machine_specs}
</market_context>

<competitive_landscape>
Direct competitors: {nearby_vending_machines}
Indirect competitors: {nearby_retail}
Substitutes: {alternative_options}
</competitive_landscape>

<our_performance>
{our_metrics}
</our_performance>

<competitive_data>
Pricing comparison: {price_comparison}
Product overlap: {product_overlap_analysis}
Estimated competitor sales: {competitor_estimates}
Customer feedback: {comparative_reviews}
</competitive_data>

<strategic_analysis_framework>
1. Competitive Positioning
   - Price leadership vs premium
   - Assortment breadth vs specialization  
   - Convenience vs experience
   - Technology vs traditional

2. Differentiation Opportunities
   - Unique products
   - Better freshness
   - Superior technology
   - Price advantages
   - Location convenience

3. Competitive Threats
   - New entrants
   - Substitute products
   - Technology disruption
   - Changing preferences

4. Strategic Responses
   - Match competitor moves
   - Differentiate further
   - Change battlefield
   - Collaborate/coexist
</strategic_analysis_framework>

<game_theory_analysis>
Consider strategic interactions:

If competitor lowers prices:
- Our response options and payoffs
- Nash equilibrium outcome
- First-mover advantages

If competitor adds products:
- Substitution effects
- Market expansion potential
- Response strategies

If new competitor enters:
- Market share impact
- Defensive strategies
- Accommodation vs competition
</game_theory_analysis>

<output_format>
{{
    "competitive_position": {{
        "market_share_estimate": float,
        "relative_price_position": "premium|parity|value",
        "differentiation_score": float,
        "competitive_advantage": ["list_of_advantages"],
        "vulnerabilities": ["list_of_weaknesses"]
    }},
    "competitor_analysis": [
        {{
            "competitor": "name_or_type",
            "threat_level": "high|medium|low",
            "strengths": ["list"],
            "weaknesses": ["list"],
            "likely_strategy": "description",
            "our_response": "recommended_action"
        }}
    ],
    "differentiation_strategy": {{
        "primary_differentiator": "what_makes_us_unique",
        "supporting_elements": ["list"],
        "customer_value_proposition": "statement",
        "implementation_tactics": [
            {{
                "tactic": "specific_action",
                "impact": "expected_result",
                "timeline": "when"
            }}
        ]
    }},
    "pricing_strategy": {{
        "recommended_approach": "premium|competitive|penetration|dynamic",
        "price_adjustments": [
            {{
                "product": "name",
                "current_price": float,
                "recommended_price": float,
                "rationale": "why"
            }}
        ],
        "expected_volume_impact": float,
        "expected_revenue_impact": float
    }},
    "product_strategy": {{
        "must_have": ["products_we_need"],
        "differentiators": ["unique_products"],
        "consider_dropping": ["underperformers"],
        "test_additions": ["experimental_products"]
    }},
    "monitoring_plan": {{
        "key_metrics": ["what_to_track"],
        "warning_signals": ["what_to_watch_for"],
        "review_frequency": "daily|weekly|monthly"
    }}
}}
</output_format>"""

    @staticmethod
    def scenario_planning_simulation() -> str:
        """Template for scenario planning and simulation"""
        return """<role>
You are a scenario planning expert simulating various future states for vending operations.
</role>

<base_case>
Current state: {current_metrics}
Current planogram: {current_configuration}
Historical trends: {trend_data}
</base_case>

<scenarios_to_simulate>
1. Best Case Scenario
   Assumptions: {best_case_assumptions}
   Probability: {best_case_probability}

2. Most Likely Scenario  
   Assumptions: {likely_assumptions}
   Probability: {likely_probability}

3. Worst Case Scenario
   Assumptions: {worst_case_assumptions}
   Probability: {worst_case_probability}

4. Black Swan Events
   Events: {black_swan_events}
   Individual probabilities: {black_swan_probabilities}
</scenarios_to_simulate>

<simulation_parameters>
Time horizon: {simulation_months} months
Monte Carlo runs: {num_simulations}
Key variables: {variable_ranges}
Correlations: {variable_correlations}
</simulation_parameters>

<decision_tree_analysis>
Decision points:
{decision_tree_structure}

For each path:
- Calculate expected value
- Assess risk/variance
- Identify critical factors
</decision_tree_analysis>

<sensitivity_factors>
Test sensitivity to:
- Price elasticity: {price_sensitivity_range}
- Weather impact: {weather_correlation}
- Competition: {competitive_response}
- Economic conditions: {economic_scenarios}
- Technology adoption: {tech_adoption_curve}
</sensitivity_factors>

<robust_strategy_criteria>
A robust strategy should:
1. Perform acceptably in all scenarios
2. Capitalize on upside opportunities
3. Limit downside risk
4. Maintain flexibility for pivots
5. Consider option value
</robust_strategy_criteria>

<output_format>
{{
    "scenario_outcomes": [
        {{
            "scenario_name": "string",
            "probability": float,
            "key_assumptions": ["list"],
            "projected_metrics": {{
                "revenue": {{
                    "month_1": float,
                    "month_3": float,
                    "month_6": float,
                    "month_12": float
                }},
                "profit_margin": float,
                "stockout_rate": float,
                "customer_satisfaction": float
            }},
            "critical_success_factors": ["list"],
            "warning_indicators": ["early_signals"]
        }}
    ],
    "monte_carlo_results": {{
        "expected_value": float,
        "standard_deviation": float,
        "percentiles": {{
            "p5": float,
            "p25": float,
            "p50": float,
            "p75": float,
            "p95": float
        }},
        "value_at_risk": {{
            "var_95": float,
            "cvar_95": float
        }}
    }},
    "sensitivity_analysis": {{
        "most_sensitive_variables": [
            {{
                "variable": "name",
                "impact_coefficient": float,
                "optimal_range": [min, max]
            }}
        ],
        "break_even_points": {{
            "variable": "threshold_value"
        }},
        "tipping_points": [
            {{
                "condition": "description",
                "threshold": float,
                "impact": "what_happens"
            }}
        ]
    }},
    "robust_strategies": [
        {{
            "strategy_name": "string",
            "description": "approach",
            "performance_across_scenarios": {{
                "best_case": float,
                "likely_case": float,
                "worst_case": float,
                "black_swan": float
            }},
            "flexibility_score": float,
            "implementation_plan": ["steps"],
            "decision_triggers": [
                {{
                    "condition": "what_to_monitor",
                    "threshold": "value",
                    "action": "what_to_do"
                }}
            ]
        }}
    ],
    "recommendations": {{
        "immediate_actions": ["high_confidence_moves"],
        "contingency_plans": [
            {{
                "trigger": "condition",
                "response": "action_plan"
            }}
        ],
        "option_preservation": ["maintain_flexibility_for"],
        "monitoring_dashboard": {{
            "leading_indicators": ["early_warning_metrics"],
            "lagging_indicators": ["confirmation_metrics"],
            "review_cadence": "frequency"
        }}
    }}
}}
</output_format>"""

    @staticmethod
    def cross_location_pattern_mining() -> str:
        """Template for discovering patterns across multiple locations"""
        return """<role>
You are a pattern recognition expert analyzing vending machine networks for insights.
</role>

<network_data>
Total locations: {num_locations}
Location types: {location_type_distribution}
Geographic spread: {geographic_coverage}
</network_data>

<location_clusters>
{location_clustering_data}
</location_clusters>

<performance_data>
{cross_location_metrics}
</performance_data>

<pattern_mining_objectives>
1. Identify successful patterns that can be replicated
2. Find location-specific optimizations
3. Discover unexpected correlations
4. Detect network effects and cannibalization
5. Uncover seasonal/temporal patterns
</pattern_mining_objectives>

<analysis_techniques>
1. Association Rule Mining
   - Find products that sell well together across locations
   - Minimum support: {min_support}
   - Minimum confidence: {min_confidence}

2. Clustering Analysis
   - Group similar performing locations
   - Features: {clustering_features}
   - Method: {clustering_algorithm}

3. Anomaly Detection
   - Identify outlier locations (good and bad)
   - Investigate root causes

4. Trend Analysis
   - Common trajectories after changes
   - Leading vs lagging locations

5. Network Effects
   - Cannibalization between nearby machines
   - Complementary placement opportunities
</analysis_techniques>

<hypothesis_testing>
Test hypotheses:
1. "Eye-level placement universally increases sales"
   - Null: No significant difference
   - Alternative: Significant increase
   - Test across all locations

2. "Category adjacency affects purchase behavior"
   - Test different adjacency patterns
   - Measure lift effects

3. "Venue type determines optimal assortment"
   - Compare performance by venue
   - Control for other factors

4. "Weather sensitivity varies by location"
   - Correlate weather with sales
   - Identify weather-resistant locations
</hypothesis_testing>

<output_format>
{{
    "universal_patterns": [
        {{
            "pattern": "description",
            "confidence": float,
            "support": float,
            "locations_confirmed": integer,
            "expected_lift": float,
            "implementation_priority": "high|medium|low"
        }}
    ],
    "location_segments": [
        {{
            "segment_name": "descriptive_label",
            "characteristics": ["defining_features"],
            "size": integer,
            "optimal_strategy": {{
                "assortment": ["recommended_products"],
                "pricing": "strategy",
                "service_frequency": "days"
            }},
            "exemplar_locations": ["top_performers"]
        }}
    ],
    "correlation_insights": [
        {{
            "variable_1": "metric_name",
            "variable_2": "metric_name",
            "correlation": float,
            "causation_hypothesis": "explanation",
            "actionable_insight": "what_to_do"
        }}
    ],
    "replication_opportunities": [
        {{
            "source_location": "high_performer",
            "success_factors": ["what_works"],
            "target_locations": ["where_to_replicate"],
            "expected_impact": {{
                "revenue_lift": float,
                "implementation_cost": float,
                "payback_days": integer
            }},
            "implementation_plan": ["steps"]
        }}
    ],
    "network_optimization": {{
        "cannibalization_pairs": [
            {{
                "location_1": "id",
                "location_2": "id",
                "overlap_percentage": float,
                "recommendation": "differentiate|relocate|maintain"
            }}
        ],
        "complementary_pairs": [
            {{
                "location_1": "id",
                "location_2": "id",
                "synergy_score": float,
                "coordination_opportunity": "description"
            }}
        ],
        "expansion_opportunities": [
            {{
                "area": "geographic_description",
                "rationale": "why_expand_here",
                "expected_performance": "metrics"
            }}
        ]
    }},
    "innovation_tests": [
        {{
            "hypothesis": "what_to_test",
            "test_locations": ["where_to_test"],
            "control_locations": ["comparison_group"],
            "success_metrics": ["how_to_measure"],
            "test_duration": "days",
            "go_no_go_criteria": "thresholds"
        }}
    ]
}}
</output_format>"""

    @staticmethod
    def visual_merchandising_optimization() -> str:
        """Template for optimizing visual appeal and psychological factors"""
        return """<role>
You are a visual merchandising psychologist optimizing vending displays for maximum appeal and sales.
</role>

<visual_context>
Machine type: {machine_model}
Display configuration: {display_layout}
Lighting: {lighting_type}
Current arrangement: {current_visual_arrangement}
</visual_context>

<psychological_principles>
1. Gestalt Principles
   - Proximity: Group related items
   - Similarity: Use consistent packaging
   - Continuity: Create visual flow
   - Closure: Complete patterns

2. Color Psychology
   - Red: Urgency, appetite stimulation
   - Blue: Trust, refreshment
   - Green: Health, natural
   - Yellow: Attention, happiness
   - Black: Premium, sophistication

3. Eye Movement Patterns
   - F-pattern scanning
   - Z-pattern scanning
   - Golden triangle focus
   - Central fixation bias

4. Decision Psychology
   - Paradox of choice (limit options)
   - Decoy effect (strategic pricing)
   - Anchoring (reference prices)
   - Social proof (bestseller tags)
</psychological_principles>

<current_visual_analysis>
Color distribution: {color_analysis}
Brand visibility: {brand_prominence}
Price point distribution: {price_visibility}
Category organization: {category_layout}
</current_visual_analysis>

<customer_journey>
1. Approach (3-5 seconds)
   - What draws attention?
   - First impression impact

2. Evaluation (5-10 seconds)
   - Scanning pattern
   - Decision factors

3. Selection (2-3 seconds)
   - Final choice drivers
   - Friction points

4. Transaction
   - Ease of purchase
   - Upsell opportunities
</customer_journey>

<visual_optimization_goals>
1. Increase stopping power (grab attention)
2. Improve navigation (find products quickly)
3. Enhance desire (make products appealing)
4. Facilitate decision (reduce choice overload)
5. Encourage exploration (discover new items)
</visual_optimization_goals>

<output_format>
{{
    "visual_assessment": {{
        "current_score": float,
        "strengths": ["what_works_well"],
        "weaknesses": ["what_needs_improvement"],
        "missed_opportunities": ["untapped_potential"]
    }},
    "color_optimization": {{
        "recommended_palette": {{
            "primary": "color_description",
            "secondary": "color_description",
            "accent": "color_description"
        }},
        "product_grouping": [
            {{
                "group_name": "category_or_theme",
                "color_scheme": "description",
                "positions": ["slots"],
                "visual_impact": "expected_effect"
            }}
        ],
        "contrast_points": ["where_to_create_contrast"]
    }},
    "layout_optimization": {{
        "hero_positions": ["premium_slots_for_featured_items"],
        "flow_pattern": {{
            "type": "F|Z|circular|custom",
            "key_positions": ["critical_slots"],
            "visual_anchors": ["attention_points"]
        }},
        "category_zones": [
            {{
                "zone": "area_description",
                "category": "product_type",
                "visual_cue": "how_to_differentiate"
            }}
        ],
        "white_space": ["where_to_create_breathing_room"]
    }},
    "psychological_tactics": [
        {{
            "tactic": "name",
            "implementation": "how_to_apply",
            "target_slots": ["where"],
            "expected_impact": "behavioral_change"
        }}
    ],
    "brand_storytelling": {{
        "narrative": "visual_story",
        "focal_points": ["key_products"],
        "supporting_cast": ["complementary_products"],
        "visual_hierarchy": ["importance_order"]
    }},
    "testing_recommendations": [
        {{
            "test_name": "description",
            "hypothesis": "expected_outcome",
            "variations": ["A", "B"],
            "metrics": ["what_to_measure"],
            "duration": "test_period"
        }}
    ],
    "implementation_plan": {{
        "immediate_changes": ["quick_wins"],
        "phased_updates": [
            {{
                "phase": integer,
                "changes": ["list"],
                "expected_impact": "metrics"
            }}
        ],
        "investment_required": {{
            "signage": float,
            "lighting": float,
            "shelving": float,
            "total": float
        }}
    }},
    "expected_results": {{
        "attention_increase": "percentage",
        "conversion_improvement": "percentage",
        "average_transaction_lift": "percentage",
        "customer_satisfaction_gain": "points"
    }}
}}
</output_format>"""

# =============================================================================
# COMPLEX REASONING CHAINS
# =============================================================================

class ChainOfThoughtPrompts:
    """Prompts that guide LLMs through complex reasoning chains"""
    
    @staticmethod
    def step_by_step_optimization() -> str:
        """Guide through systematic optimization process"""
        return """<systematic_optimization>

Let's optimize this planogram step by step.

STEP 1: Analyze Current State
First, I need to understand what we're working with:
- Current revenue: ${current_revenue}/day
- Utilization: {filled_slots}/{total_slots} slots
- Top performers: {top_products}
- Problem areas: {underperformers}

STEP 2: Identify Constraints
What limits our options?
- Physical: {physical_constraints}
- Business rules: {business_rules}
- Must-keep products: {protected_products}

STEP 3: Calculate Opportunity Scores
For each potential change:
Opportunity = (Revenue_Gain × Probability_Success) - (Implementation_Cost + Risk)

Empty Slots (Highest Priority):
{empty_slot_analysis}

Underperforming Slots:
{underperformer_analysis}

STEP 4: Generate Candidate Solutions
Solution 1: Fill all empty slots with top sellers
- Pros: Guaranteed revenue increase
- Cons: Reduces variety
- Expected impact: +${solution_1_impact}/day

Solution 2: Category-balanced approach
- Pros: Maintains variety, reduces stockouts
- Cons: Lower immediate revenue
- Expected impact: +${solution_2_impact}/day

Solution 3: Data-driven optimization
- Pros: Based on actual performance
- Cons: May miss new opportunities
- Expected impact: +${solution_3_impact}/day

STEP 5: Evaluate Trade-offs
Comparing solutions on multiple criteria:
- Revenue potential
- Implementation ease
- Risk level
- Long-term sustainability

STEP 6: Select Optimal Approach
Based on the analysis, the recommended approach is:
{recommended_approach}

STEP 7: Detail Implementation
Specific changes to make:
{detailed_changes}

STEP 8: Define Success Metrics
How we'll measure success:
{success_metrics}

STEP 9: Plan Contingencies
If performance doesn't meet expectations:
{contingency_plans}

STEP 10: Document Learning
Key insights for future optimization:
{lessons_learned}

</systematic_optimization>"""

    @staticmethod
    def root_cause_tree() -> str:
        """Tree-based root cause analysis"""
        return """<root_cause_analysis>

Problem: {problem_statement}

Let me trace through possible causes systematically:

Level 1: Major Categories
├── Product Issues
│   ├── Quality/Freshness
│   ├── Pricing
│   └── Assortment
├── Placement Issues
│   ├── Visibility
│   ├── Accessibility
│   └── Organization
├── Machine Issues
│   ├── Technical Problems
│   ├── Temperature
│   └── Appearance
└── External Factors
    ├── Competition
    ├── Seasonality
    └── Location Changes

Level 2: Investigating Product Issues
├── Quality/Freshness
│   ├── Check: Expiration dates → {expiration_check}
│   ├── Check: Customer complaints → {complaint_check}
│   └── Finding: {quality_finding}
├── Pricing
│   ├── Check: Price vs competition → {price_comparison}
│   ├── Check: Recent changes → {price_history}
│   └── Finding: {pricing_finding}
└── Assortment
    ├── Check: Missing favorites → {assortment_gaps}
    ├── Check: Poor performers → {slow_movers}
    └── Finding: {assortment_finding}

Level 3: Deep Dive on Most Likely Cause
{detailed_investigation}

Root Cause Identification:
Primary Cause: {primary_cause}
Contributing Factors: {contributing_factors}
Evidence Supporting: {supporting_evidence}

Recommended Actions:
1. Immediate: {immediate_action}
2. Short-term: {short_term_action}
3. Long-term: {long_term_action}

</root_cause_analysis>"""

# =============================================================================
# SELF-IMPROVING PROMPTS
# =============================================================================

class SelfImprovingPrompts:
    """Prompts that learn and improve from feedback"""
    
    @staticmethod
    def iterative_refinement() -> str:
        """Template for iterative improvement cycles"""
        return """<iterative_optimization>

ITERATION {iteration_number}

Previous Result:
{previous_result}

Performance vs Target:
- Target: {target_metric}
- Achieved: {achieved_metric}
- Gap: {performance_gap}

Learning from Last Iteration:
- What worked: {successful_elements}
- What didn't work: {failed_elements}
- Unexpected outcomes: {surprises}

Hypothesis for Improvement:
Based on the results, I hypothesize that:
{improvement_hypothesis}

Refined Approach:
{refined_strategy}

Expected Improvement:
{expected_new_performance}

Confidence Level: {confidence_score}

Stop Condition Check:
- Target met? {target_met}
- Improvement plateau? {plateaued}
- Maximum iterations? {max_iterations_reached}

Next Steps:
{next_iteration_plan}

</iterative_optimization>"""

    @staticmethod
    def meta_learning() -> str:
        """Template for learning across multiple optimizations"""
        return """<meta_learning>

Optimization History:
{historical_optimizations}

Pattern Recognition:
Across {num_optimizations} optimizations, I observe:

1. Successful Patterns:
   {successful_patterns}

2. Failed Patterns:
   {failed_patterns}

3. Context Dependencies:
   {context_patterns}

Learned Heuristics:
{derived_rules}

Confidence Calibration:
- When I predicted high confidence: {high_confidence_accuracy}
- When I predicted medium confidence: {medium_confidence_accuracy}
- When I predicted low confidence: {low_confidence_accuracy}

Bias Detection:
- Systematic overestimation: {overestimation_bias}
- Systematic underestimation: {underestimation_bias}
- Context-specific biases: {contextual_biases}

Improved Decision Framework:
{updated_framework}

Generalized Insights:
{transferable_knowledge}

</meta_learning>"""

# =============================================================================
# ERROR RECOVERY PROMPTS
# =============================================================================

class ErrorRecoveryPrompts:
    """Prompts for handling errors and edge cases"""
    
    @staticmethod
    def graceful_degradation() -> str:
        """Template for handling incomplete or invalid data"""
        return """<error_handling>

Data Quality Assessment:
- Completeness: {data_completeness}%
- Validity: {data_validity}%
- Consistency: {data_consistency}%

Missing Critical Data:
{missing_data_list}

Available Fallbacks:
1. Historical averages: {historical_data_available}
2. Similar locations: {comparable_data_available}
3. Industry benchmarks: {benchmark_data_available}
4. Rule-based defaults: {rules_available}

Degradation Strategy:
Given the data limitations, I will:

Level 1 (Preferred): {level_1_approach}
- Data required: {level_1_requirements}
- Confidence: {level_1_confidence}

Level 2 (Fallback): {level_2_approach}
- Data required: {level_2_requirements}
- Confidence: {level_2_confidence}

Level 3 (Minimum): {level_3_approach}
- Data required: {level_3_requirements}
- Confidence: {level_3_confidence}

Selected Approach: {selected_level}
Rationale: {selection_reasoning}

Caveats and Limitations:
{important_caveats}

Recommendations for Data Improvement:
{data_collection_priorities}

</error_handling>"""

# =============================================================================
# PROMPT COMPOSITION UTILITIES
# =============================================================================

class PromptComposer:
    """Utilities for composing complex prompts from components"""
    
    @staticmethod
    def combine_prompts(
        base_template: str,
        reasoning_pattern: ReasoningPattern,
        error_handling: bool = True,
        self_improvement: bool = False
    ) -> str:
        """Combine multiple prompt components into a comprehensive prompt"""
        
        components = [base_template]
        
        # Add reasoning pattern
        if reasoning_pattern == ReasoningPattern.CHAIN_OF_THOUGHT:
            components.append(ChainOfThoughtPrompts.step_by_step_optimization())
        elif reasoning_pattern == ReasoningPattern.TREE_OF_THOUGHT:
            components.append(ChainOfThoughtPrompts.root_cause_tree())
        
        # Add error handling if needed
        if error_handling:
            components.append(ErrorRecoveryPrompts.graceful_degradation())
        
        # Add self-improvement if needed
        if self_improvement:
            components.append(SelfImprovingPrompts.iterative_refinement())
        
        return "\n\n".join(components)
    
    @staticmethod
    def add_few_shot_examples(
        template: str,
        examples: List[Dict]
    ) -> str:
        """Add few-shot examples to improve performance"""
        
        example_text = "<examples>\n"
        for i, example in enumerate(examples, 1):
            example_text += f"Example {i}:\n"
            example_text += f"Input: {json.dumps(example['input'], indent=2)}\n"
            example_text += f"Output: {json.dumps(example['output'], indent=2)}\n\n"
        example_text += "</examples>\n\n"
        
        return example_text + template
    
    @staticmethod
    def add_constraints(
        template: str,
        constraints: List[str]
    ) -> str:
        """Add specific constraints to the prompt"""
        
        constraint_text = "<constraints>\n"
        for constraint in constraints:
            constraint_text += f"- {constraint}\n"
        constraint_text += "</constraints>\n\n"
        
        return template.replace("<constraints>", constraint_text)

# =============================================================================
# PROMPT VALIDATION
# =============================================================================

class PromptValidator:
    """Validate prompts for completeness and quality"""
    
    @staticmethod
    def validate_template(template: str) -> Dict:
        """Check if template has all required components"""
        
        issues = []
        warnings = []
        
        # Check for required sections
        required_sections = ['<role>', '<task>', '<output_format>']
        for section in required_sections:
            if section not in template:
                issues.append(f"Missing required section: {section}")
        
        # Check for clear output format
        if '<output_format>' in template and '{{' not in template:
            warnings.append("Output format should include JSON structure")
        
        # Check for variable placeholders
        import re
        placeholders = re.findall(r'\{(\w+)\}', template)
        if not placeholders:
            warnings.append("No variable placeholders found")
        
        # Check prompt length
        if len(template) > 10000:
            warnings.append("Template may be too long for some models")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'placeholders': placeholders,
            'estimated_tokens': len(template) // 4
        }

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def example_advanced_usage():
    """Examples of using advanced prompt templates"""
    
    # Example 1: Multi-objective optimization
    template = AdvancedPromptTemplates.multi_objective_optimization()
    data = {
        'revenue_weight': 0.4,
        'satisfaction_weight': 0.2,
        'turnover_weight': 0.2,
        'variety_weight': 0.1,
        'efficiency_weight': 0.1,
        'current_revenue': 285.50,
        'nps_score': 72,
        'avg_inventory_days': 4.5,
        'unique_products': 45,
        'categories': 8,
        'service_minutes': 28,
        'current_planogram_analysis': '{...}',
        'physical_constraints': '{...}',
        'business_rules': '{...}',
        'compliance_requirements': '{...}'
    }
    prompt = template.format(**data)
    
    # Example 2: Compose complex prompt with reasoning
    composer = PromptComposer()
    complex_prompt = composer.combine_prompts(
        base_template=AdvancedPromptTemplates.competitive_intelligence_analysis(),
        reasoning_pattern=ReasoningPattern.CHAIN_OF_THOUGHT,
        error_handling=True,
        self_improvement=True
    )
    
    # Example 3: Add few-shot examples
    examples = [
        {
            'input': {'scenario': 'empty_slots', 'count': 5},
            'output': {'recommendation': 'fill_with_top_sellers', 'impact': '+$25/day'}
        }
    ]
    enhanced_prompt = composer.add_few_shot_examples(template, examples)
    
    # Example 4: Validate prompt
    validator = PromptValidator()
    validation_result = validator.validate_template(template)
    print(f"Prompt validation: {validation_result}")

if __name__ == "__main__":
    example_advanced_usage()