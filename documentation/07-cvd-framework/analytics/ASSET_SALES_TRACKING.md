# Asset Sales Tracking


## Metadata
- **ID**: 07_CVD_FRAMEWORK_ANALYTICS_ASSET_SALES_TRACKING
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #cvd-specific #data-exchange #debugging #device-management #dex-parser #domain #integration #logistics #machine-learning #metrics #optimization #performance #quality-assurance #reporting #route-management #testing #troubleshooting #vending #vending-machine
- **Intent**: Documentation for Asset Sales Tracking
- **Audience**: managers
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/07-cvd-framework/analytics/
- **Category**: Analytics
- **Search Keywords**: ###, analysis, analytics, anomaly, asset, benchmarking, comparative, cooler, detection, device, dex, interactive, location-based, monitoring, performance

The CVD asset sales tracking system provides comprehensive device-level performance analytics, enabling fleet managers to monitor individual vending machine performance, identify optimization opportunities, and make data-driven operational decisions.

## Overview

Asset sales tracking focuses on individual device performance analysis, providing detailed insights into revenue generation, sales patterns, customer behavior, and operational efficiency at the device level across the entire fleet.

### Key Capabilities
- **Device Performance Monitoring**: Track revenue, units sold, and transaction patterns per device
- **Location-Based Analysis**: Performance comparison by geographic location and venue type
- **Time-Series Analytics**: Historical trend analysis with configurable date ranges
- **Comparative Benchmarking**: Performance comparison against fleet averages and peer devices
- **Interactive Visualization**: Real-time charts and graphs with drill-down capabilities

## Technical Implementation

### Frontend Interface (asset-sales.html)

#### Dashboard Structure
```html
<!-- Asset Sales Dashboard Layout -->
<div class="analytics-dashboard">
    <div class="controls-panel">
        <!-- Date range selectors -->
        <!-- Device filters -->
        <!-- Location filters -->
        <!-- Export controls -->
    </div>
    
    <div class="metrics-overview">
        <!-- KPI cards -->
        <!-- Performance summaries -->
        <!-- Fleet comparisons -->
    </div>
    
    <div class="device-table">
        <!-- Detailed device performance table -->
        <!-- Sortable columns -->
        <!-- Interactive row selection -->
    </div>
    
    <div class="visualization-panel">
        <!-- Performance charts -->
        <!-- Trend analysis -->
        <!-- Geographic mapping -->
    </div>
</div>
```

#### Data Loading and Processing
```javascript
// Asset Sales Data Management
class AssetSalesAnalytics {
    constructor() {
        this.devices = [];
        this.dateRange = this.getDefaultDateRange();
        this.filters = new Map();
        this.chartInstances = new Map();
    }
    
    async loadDevicePerformance() {
        try {
            const response = await fetch('/api/analytics/asset-sales', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    start_date: this.dateRange.start,
                    end_date: this.dateRange.end,
                    filters: Object.fromEntries(this.filters)
                })
            });
            
            const data = await response.json();
            this.devices = data.devices;
            this.updateDashboard();
            
        } catch (error) {
            console.error('Failed to load asset sales data:', error);
            this.showError('Unable to load performance data');
        }
    }
}
```

### Backend API Integration

#### Asset Sales Analytics Endpoint
```python
@app.route('/api/analytics/asset-sales', methods=['POST'])
def get_asset_sales_analytics():
    """Generate comprehensive asset sales analytics"""
    data = request.json
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    filters = data.get('filters', {})
    
    # Build device performance query
    query = """
    SELECT 
        d.id as device_id,
        d.asset,
        d.cooler,
        l.name as location_name,
        l.address,
        dt.name as device_type,
        COUNT(s.id) as total_transactions,
        SUM(s.sale_units) as total_units,
        SUM(s.sale_cash) as total_revenue,
        AVG(s.sale_cash) as avg_transaction_value,
        MIN(s.created_at) as first_sale,
        MAX(s.created_at) as last_sale
    FROM devices d
    LEFT JOIN locations l ON d.location_id = l.id
    LEFT JOIN device_types dt ON d.device_type_id = dt.id
    LEFT JOIN sales s ON d.id = s.device_id 
        AND s.created_at BETWEEN ? AND ?
    WHERE d.deleted_at IS NULL
    GROUP BY d.id, d.asset, d.cooler, l.name, l.address, dt.name
    ORDER BY total_revenue DESC
    """
    
    cursor.execute(query, (start_date, end_date))
    devices = [dict(row) for row in cursor.fetchall()]
    
    # Calculate additional metrics
    for device in devices:
        device.update(calculate_device_metrics(device, start_date, end_date))
    
    return {
        'devices': devices,
        'fleet_summary': calculate_fleet_summary(devices),
        'time_period': {'start': start_date, 'end': end_date}
    }
```

#### Performance Metrics Calculation
```python
def calculate_device_metrics(device, start_date, end_date):
    """Calculate comprehensive performance metrics for a device"""
    device_id = device['device_id']
    total_revenue = device['total_revenue'] or 0
    total_units = device['total_units'] or 0
    
    # Calculate time-based metrics
    date_range = (datetime.strptime(end_date, '%Y-%m-%d') - 
                  datetime.strptime(start_date, '%Y-%m-%d')).days + 1
    
    daily_revenue = total_revenue / date_range if date_range > 0 else 0
    daily_units = total_units / date_range if date_range > 0 else 0
    
    # Get product performance for device
    product_performance = get_device_product_performance(device_id, start_date, end_date)
    
    # Calculate performance trends
    performance_trend = get_device_performance_trend(device_id, start_date, end_date)
    
    return {
        'daily_revenue': round(daily_revenue, 2),
        'daily_units': round(daily_units, 2),
        'revenue_per_unit': round(total_revenue / total_units, 2) if total_units > 0 else 0,
        'active_days': len(performance_trend),
        'top_products': product_performance[:5],
        'performance_trend': performance_trend,
        'performance_score': calculate_performance_score(device, daily_revenue, daily_units)
    }
```

## Device Performance Analysis

### Revenue Tracking
```javascript
// Revenue Analysis Components
const revenueMetrics = {
    'total_revenue': 'Total revenue generated during time period',
    'daily_average': 'Average revenue per day',
    'revenue_trend': 'Revenue trend over time period',
    'revenue_per_transaction': 'Average transaction value',
    'peak_performance_days': 'Highest revenue generating days'
};

// Revenue Trend Visualization
function createRevenueTrendChart(deviceData) {
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: deviceData.performance_trend.map(d => d.date),
            datasets: [{
                label: 'Daily Revenue',
                data: deviceData.performance_trend.map(d => d.revenue),
                borderColor: '#006dfe',
                backgroundColor: 'rgba(0, 109, 254, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            interaction: { intersect: false },
            plugins: {
                title: {
                    display: true,
                    text: `Revenue Trend - ${deviceData.asset}`
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}
```

### Sales Volume Analysis
```python
# Sales Volume Tracking
def get_device_volume_analysis(device_id, start_date, end_date):
    """Analyze sales volume patterns for a device"""
    query = """
    SELECT 
        DATE(s.created_at) as sale_date,
        SUM(s.sale_units) as daily_units,
        COUNT(DISTINCT s.id) as daily_transactions,
        AVG(s.sale_units) as avg_units_per_transaction,
        MIN(TIME(s.created_at)) as first_sale_time,
        MAX(TIME(s.created_at)) as last_sale_time
    FROM sales s
    WHERE s.device_id = ? 
    AND s.created_at BETWEEN ? AND ?
    GROUP BY DATE(s.created_at)
    ORDER BY sale_date
    """
    
    cursor.execute(query, (device_id, start_date, end_date))
    volume_data = [dict(row) for row in cursor.fetchall()]
    
    # Calculate volume insights
    return {
        'daily_volume': volume_data,
        'peak_volume_day': max(volume_data, key=lambda x: x['daily_units']),
        'average_daily_volume': sum(d['daily_units'] for d in volume_data) / len(volume_data),
        'volume_consistency': calculate_volume_consistency(volume_data),
        'hourly_patterns': get_hourly_sales_patterns(device_id, start_date, end_date)
    }
```

### Location Performance Analysis
```javascript
// Geographic Performance Visualization
class LocationPerformanceMap {
    constructor(containerId) {
        this.map = L.map(containerId).setView([39.8283, -98.5795], 4);
        this.deviceMarkers = [];
        this.initializeMap();
    }
    
    initializeMap() {
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
    }
    
    updateDeviceMarkers(devices) {
        // Clear existing markers
        this.deviceMarkers.forEach(marker => this.map.removeLayer(marker));
        this.deviceMarkers = [];
        
        devices.forEach(device => {
            if (device.latitude && device.longitude) {
                const marker = this.createDeviceMarker(device);
                marker.addTo(this.map);
                this.deviceMarkers.push(marker);
            }
        });
        
        // Fit map to show all markers
        if (this.deviceMarkers.length > 0) {
            const group = new L.featureGroup(this.deviceMarkers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }
    
    createDeviceMarker(device) {
        const icon = this.getPerformanceIcon(device.performance_score);
        
        return L.marker([device.latitude, device.longitude], { icon })
            .bindPopup(this.createPopupContent(device));
    }
    
    createPopupContent(device) {
        return `
            <div class="device-popup">
                <h4>${device.asset}</h4>
                <p><strong>Location:</strong> ${device.location_name}</p>
                <p><strong>Revenue:</strong> $${device.total_revenue.toFixed(2)}</p>
                <p><strong>Daily Avg:</strong> $${device.daily_revenue.toFixed(2)}</p>
                <p><strong>Units Sold:</strong> ${device.total_units}</p>
                <button onclick="viewDeviceDetails(${device.device_id})">
                    View Details
                </button>
            </div>
        `;
    }
}
```

## Comparative Analysis

### Fleet Benchmarking
```python
def calculate_fleet_benchmarks(devices):
    """Calculate fleet-wide performance benchmarks"""
    active_devices = [d for d in devices if d['total_revenue'] > 0]
    
    if not active_devices:
        return {}
    
    revenues = [d['total_revenue'] for d in active_devices]
    daily_revenues = [d['daily_revenue'] for d in active_devices]
    units = [d['total_units'] for d in active_devices]
    
    return {
        'fleet_summary': {
            'total_devices': len(devices),
            'active_devices': len(active_devices),
            'total_fleet_revenue': sum(revenues),
            'average_device_revenue': statistics.mean(revenues),
            'median_device_revenue': statistics.median(revenues),
            'top_performer': max(active_devices, key=lambda x: x['total_revenue']),
            'bottom_performer': min(active_devices, key=lambda x: x['total_revenue'])
        },
        'benchmarks': {
            'revenue_quartiles': {
                'q1': statistics.quantiles(revenues, n=4)[0],
                'q2': statistics.median(revenues),
                'q3': statistics.quantiles(revenues, n=4)[2]
            },
            'daily_revenue_avg': statistics.mean(daily_revenues),
            'units_per_device_avg': statistics.mean(units),
            'performance_distribution': calculate_performance_distribution(active_devices)
        }
    }
```

### Performance Ranking System
```javascript
// Device Performance Ranking
function calculatePerformanceRanking(devices) {
    // Multi-factor performance scoring
    devices.forEach(device => {
        device.performance_score = calculateCompositeScore({
            revenue_score: normalizeScore(device.total_revenue, 'revenue'),
            consistency_score: calculateConsistencyScore(device.performance_trend),
            growth_score: calculateGrowthScore(device.performance_trend),
            efficiency_score: device.total_revenue / (device.total_units || 1)
        });
    });
    
    // Sort by performance score
    return devices.sort((a, b) => b.performance_score - a.performance_score)
        .map((device, index) => ({
            ...device,
            fleet_rank: index + 1,
            percentile: ((devices.length - index) / devices.length) * 100
        }));
}

function calculateCompositeScore(scores) {
    const weights = {
        revenue_score: 0.4,
        consistency_score: 0.25,
        growth_score: 0.2,
        efficiency_score: 0.15
    };
    
    return Object.entries(weights)
        .reduce((total, [metric, weight]) => total + (scores[metric] * weight), 0);
}
```

## Advanced Analytics Features

### Trend Analysis
```python
def analyze_performance_trends(device_id, start_date, end_date):
    """Analyze performance trends and patterns"""
    daily_data = get_daily_performance_data(device_id, start_date, end_date)
    
    # Calculate trend metrics
    revenue_trend = calculate_linear_trend([d['revenue'] for d in daily_data])
    volume_trend = calculate_linear_trend([d['units'] for d in daily_data])
    
    # Identify patterns
    seasonal_patterns = identify_seasonal_patterns(daily_data)
    day_of_week_patterns = analyze_day_of_week_patterns(daily_data)
    
    return {
        'trends': {
            'revenue_trend': revenue_trend,
            'volume_trend': volume_trend,
            'trend_direction': 'increasing' if revenue_trend['slope'] > 0 else 'decreasing'
        },
        'patterns': {
            'seasonal': seasonal_patterns,
            'weekly': day_of_week_patterns,
            'peak_days': identify_peak_performance_days(daily_data),
            'low_performance_days': identify_low_performance_days(daily_data)
        },
        'forecasting': {
            'next_30_days': forecast_performance(daily_data, 30),
            'confidence_interval': calculate_forecast_confidence(daily_data)
        }
    }
```

### Anomaly Detection
```javascript
// Performance Anomaly Detection
class PerformanceAnomalyDetector {
    constructor(threshold = 2.5) {
        this.threshold = threshold; // Standard deviations from mean
        this.anomalies = [];
    }
    
    detectAnomalies(deviceData) {
        const revenues = deviceData.performance_trend.map(d => d.revenue);
        const mean = this.calculateMean(revenues);
        const stdDev = this.calculateStandardDeviation(revenues, mean);
        
        this.anomalies = deviceData.performance_trend
            .map((day, index) => ({
                date: day.date,
                revenue: day.revenue,
                z_score: Math.abs(day.revenue - mean) / stdDev,
                is_anomaly: Math.abs(day.revenue - mean) / stdDev > this.threshold
            }))
            .filter(day => day.is_anomaly);
        
        return this.anomalies;
    }
    
    categorizeAnomalies() {
        return this.anomalies.map(anomaly => ({
            ...anomaly,
            type: anomaly.z_score > this.threshold ? 'high_performance' : 'low_performance',
            severity: this.calculateSeverity(anomaly.z_score)
        }));
    }
}
```

## Export and Reporting

### Data Export Functionality
```javascript
// Asset Sales Report Export
class AssetSalesExporter {
    constructor() {
        this.exportFormats = ['csv', 'excel', 'pdf'];
    }
    
    async exportDevicePerformance(devices, format, options = {}) {
        const exportData = this.prepareExportData(devices, options);
        
        switch (format) {
            case 'csv':
                return this.exportToCSV(exportData);
            case 'excel':
                return this.exportToExcel(exportData);
            case 'pdf':
                return this.exportToPDF(exportData);
            default:
                throw new Error(`Unsupported export format: ${format}`);
        }
    }
    
    prepareExportData(devices, options) {
        return devices.map(device => ({
            'Asset ID': device.asset,
            'Location': device.location_name,
            'Device Type': device.device_type,
            'Total Revenue': device.total_revenue,
            'Daily Average': device.daily_revenue,
            'Total Units': device.total_units,
            'Transactions': device.total_transactions,
            'Avg Transaction': device.revenue_per_unit,
            'Performance Score': device.performance_score,
            'Fleet Rank': device.fleet_rank,
            'Top Product': device.top_products[0]?.product_name || 'N/A'
        }));
    }
}
```

The asset sales tracking system provides comprehensive device-level analytics that enable fleet managers to optimize individual machine performance, identify trends and opportunities, and make data-driven decisions that maximize revenue and operational efficiency across their entire vending machine fleet.