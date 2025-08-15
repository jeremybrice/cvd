"""
Real-time Planogram Assistant Prompt Templates
Provides contextual AI assistance while merchandisers work on planograms
"""

REALTIME_ANALYSIS_PROMPT = """<planogram_context>
Device: {device_name} (Asset: {asset_number})
Location: {location}
Cabinet: {cabinet_type} ({rows}x{columns})
Current Capacity Utilization: {capacity_percent}%
Empty Slots: {empty_slots}
Last Service: {last_service_date}
</planogram_context>

<current_action>
User is: {user_action}
Product Being Placed: {product_name}
Target Slot: {slot_position}
</current_action>

<performance_data>
{sales_metrics}
</performance_data>

<merchandising_rules>
1. Eye-level slots (rows B-C) should have high-velocity items
2. Complementary products should be adjacent
3. Price points should vary vertically
4. Perishables need accessible positions
5. Heavy items go in bottom rows
</merchandising_rules>

Analyze this placement decision and provide:
1. Placement score (0-100) with reasoning
2. Adjacent product recommendations
3. Potential issues or conflicts
4. Alternative slot suggestions if score < 70

Format as JSON: {
    "placement_score": int,
    "reasoning": str,
    "adjacent_recommendations": [{"slot": str, "product": str, "reason": str}],
    "issues": [str],
    "alternatives": [{"slot": str, "score": int, "reason": str}]
}"""

PATTERN_RECOGNITION_PROMPT = """<historical_patterns>
Device Category: {device_category}
Location Type: {location_type}
Time Period: {time_period}
</historical_patterns>

<successful_planograms>
{top_performing_layouts}
</successful_planograms>

<current_planogram>
{current_layout}
</current_planogram>

Identify patterns from successful planograms that could improve the current layout:

1. Product placement patterns that drive sales
2. Category arrangements that increase basket size
3. Seasonal adjustments needed
4. Cross-merchandising opportunities

Provide specific, actionable recommendations with expected impact.
Format response as structured JSON with confidence scores."""

CONSTRAINT_VALIDATION_PROMPT = """<physical_constraints>
Cabinet Temperature: {temperature_zone}
Shelf Weight Limits: {weight_limits}
Product Dimensions: {product_dimensions}
Slot Dimensions: {slot_dimensions}
</physical_constraints>

<business_constraints>
Vendor Requirements: {vendor_requirements}
Pricing Rules: {pricing_rules}
Promotional Items: {promotional_items}
Par Level Requirements: {par_levels}
</business_constraints>

<proposed_change>
{change_description}
</proposed_change>

Validate this planogram change against all constraints:
1. Physical compatibility
2. Business rule compliance
3. Regulatory requirements
4. Operational feasibility

Return validation result with specific violations if any."""