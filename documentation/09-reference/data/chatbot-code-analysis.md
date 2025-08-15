# Chatbot API Code Location Analysis

## **Frontend Data Collection Code**

### **Location**: `/home/jbrice/Projects/365/index.html` (lines 788-817)
```javascript
async function getBusinessContext() {
    try {
        // Get comprehensive data from all APIs
        const [weeklyMetrics, timeline, achievements, topPerformers, salesSummary, devices] = await Promise.all([
            chatApi.makeRequest('GET', '/metrics/weekly'),
            chatApi.makeRequest('GET', '/metrics/timeline'),
            chatApi.makeRequest('GET', '/metrics/achievements'),
            chatApi.makeRequest('GET', '/metrics/top-performers'),
            chatApi.makeRequest('GET', '/sales/summary'),
            chatApi.makeRequest('GET', '/devices')
        ]);
```

## **Backend API Endpoints Used by Chatbot**

### **1. Weekly Metrics API**
- **Location**: `app.py:3967-4045`
- **Endpoint**: `GET /api/metrics/weekly`
- **Function**: `get_weekly_metrics()`
- **Data Provided**:
  - Current week vs previous week revenue comparison
  - Transaction counts and growth percentages
  - Weekly performance calculations

### **2. Timeline Metrics API**
- **Location**: `app.py:4046-4091`
- **Endpoint**: `GET /api/metrics/timeline`
- **Function**: `get_growth_timeline()`
- **Data Provided**:
  - 6-month revenue timeline
  - Monthly growth trends
  - Historical performance data

### **3. Achievements API**
- **Location**: `app.py:4092-4145`
- **Endpoint**: `GET /api/metrics/achievements`
- **Function**: `get_achievements()`
- **Data Provided**:
  - Monthly revenue targets ($4000)
  - Achievement progress percentages
  - Success/milestone tracking

### **4. Top Performers API**
- **Location**: `app.py:4146-4257`
- **Endpoint**: `GET /api/metrics/top-performers`
- **Function**: `get_top_performers()`
- **Data Provided**:
  - Top performing device by revenue
  - Top performing location by revenue
  - Weekly performance rankings

### **5. Sales Summary API**
- **Location**: `app.py:3488-3583`
- **Endpoint**: `GET /api/sales/summary`
- **Function**: `get_sales_summary()`
- **Data Provided**:
  - Aggregated sales by device, product, or time period
  - Transaction counts and revenue totals
  - Flexible grouping and filtering

### **6. Devices API**
- **Location**: `app.py:1094-1164`
- **Endpoint**: `GET /api/devices`
- **Function**: `get_devices()`
- **Data Provided**:
  - Complete device fleet information
  - Cabinet configurations and layouts
  - Device metrics and status

## **Main Chat Processing Code**

### **Location**: `app.py:4258-4418`
- **Endpoint**: `POST /api/chat`
- **Function**: `chat_with_ai()`

### **Key Processing Steps**:

1. **API Key Validation** (lines 4266-4270)
```python
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    return jsonify({
        'response': 'AI chat is not configured. Please set the ANTHROPIC_API_KEY environment variable to enable AI assistance.'
    })
```

2. **Context Processing** (lines 4279-4286)
```python
weekly_metrics = context.get('weekly', {})
achievements = context.get('achievements', {})
performers = context.get('performers', [])
sales_summary = context.get('salesSummary', {})
devices = context.get('devices', [])
page_context = context.get('pageContext', {})
```

3. **Additional Data Queries** (lines 4288-4307)
```python
# Recent sales (last 7 days)
recent_sales = cursor.execute('''
    SELECT COUNT(*) as transactions, SUM(sale_cash) as revenue
    FROM sales 
    WHERE created_at >= datetime('now', '-7 days')
''').fetchone()

# Top selling products
top_products = cursor.execute('''
    SELECT p.name, SUM(s.sale_units) as units_sold, SUM(s.sale_cash) as revenue
    FROM sales s
    JOIN products p ON s.product_id = p.id
    WHERE s.created_at >= datetime('now', '-30 days')
    GROUP BY p.id, p.name
    ORDER BY units_sold DESC
    LIMIT 3
''').fetchall()
```

4. **Knowledge Base Integration** (lines 4309-4354)
```python
# Get page-specific knowledge
current_page = page_context.get('currentPage', '')
page_knowledge = get_page_knowledge(current_page)

# Add navigation help for general questions
nav_help = get_navigation_help()
```

5. **Anthropic API Call** (lines 4385-4409)
```python
client = anthropic.Anthropic(api_key=api_key)

response = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=150,
    messages=[
        {
            "role": "user",
            "content": f"""You are a comprehensive assistant for a small vending machine operation..."""
        }
    ]
)
```

## **Knowledge Base System**

### **Location**: `knowledge_base.py`
- **Page Knowledge**: Lines 6-225 (comprehensive application guidance)
- **Navigation Guide**: Lines 227-263 (menu and URL navigation)
- **Common Workflows**: Lines 265-340 (step-by-step processes)
- **Troubleshooting**: Lines 342-392 (problem resolution)
- **Feature Reference**: Lines 394-436 (functionality documentation)

### **Key Functions**:
- `get_page_knowledge()`: Current page context
- `get_navigation_help()`: Navigation guidance
- `get_workflow_help()`: Task workflows
- `get_troubleshooting_help()`: Problem solving
- `search_knowledge()`: Knowledge base search

## **Database Tables Accessed**

The chatbot leverages data from these core tables:
- **`sales`**: Transaction data, revenue, units sold
- **`devices`**: Device fleet, configurations, metrics
- **`products`**: Product catalog, categories, pricing
- **`locations`**: Location names and assignments
- **`routes`**: Route assignments and planning
- **`planograms`** & **`planogram_slots`**: Product layouts

## **Data Flow Summary**

1. **Frontend** (`index.html:788-817`) → Collects business context via 6 parallel API calls
2. **Backend** (`app.py:4258-4418`) → Processes context + additional queries + knowledge base
3. **Anthropic API** → Receives complete business + system context
4. **Response** → Contextual business intelligence with actionable recommendations

The chatbot has comprehensive access to all operational data through these well-defined API endpoints and processes it through a sophisticated knowledge base system to provide intelligent, contextual responses.