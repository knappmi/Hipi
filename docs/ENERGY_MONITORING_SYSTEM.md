# Energy Monitoring System

A comprehensive energy monitoring system that tracks device consumption, calculates costs, and provides insights.

## ✅ Implemented Features

### 1. Energy Consumption Tracking
- **Device Readings**: Record power consumption for each device
- **Real-time Monitoring**: Track current power consumption
- **Historical Data**: Store energy readings over time
- **Multi-device Support**: Track multiple devices simultaneously

### 2. Energy Profiles
- **Device Profiles**: Store device power ratings
- **Rated Power**: Manufacturer's rated power consumption
- **Typical Power**: Typical operating power
- **Standby Power**: Standby/off power consumption
- **Cost Configuration**: Per-device or global cost per kWh

### 3. Energy Analytics
- **Daily Summaries**: Daily energy consumption and cost
- **Device Breakdown**: Energy consumption by device
- **Peak Power Tracking**: Track peak power consumption
- **Time Period Analysis**: Calculate consumption for any time period

### 4. Energy Insights
- **Weekly/Monthly Reports**: Aggregate consumption over time
- **Average Daily Consumption**: Calculate averages
- **Top Consuming Devices**: Identify energy hogs
- **Cost Analysis**: Total and average costs

### 5. Energy Alerts
- **High Consumption Alerts**: Alert when consumption exceeds threshold
- **Threshold Alerts**: Custom threshold monitoring
- **Alert Management**: Create, acknowledge, and manage alerts

### 6. Voice Integration
- **Energy Tool**: Registered with voice agent (11 tools total)
- **Voice Queries**: Natural language energy questions
- **Intent Recognition**: Energy-related intents

## API Endpoints

### Readings
- `POST /api/v1/energy/readings` - Record energy reading
- `GET /api/v1/energy/readings/{device_id}` - Get device readings

### Current Power
- `GET /api/v1/energy/current` - Get total current power
- `GET /api/v1/energy/current?device_id={id}` - Get device current power

### Consumption
- `GET /api/v1/energy/consumption/{device_id}` - Calculate consumption

### Summaries
- `GET /api/v1/energy/summary` - Get daily summary
- `GET /api/v1/energy/summary?date={date}` - Get summary for date

### Insights
- `GET /api/v1/energy/insights?days={n}` - Get energy insights

### Profiles
- `POST /api/v1/energy/profiles` - Create device profile

### Alerts
- `POST /api/v1/energy/alerts` - Create energy alert

## Voice Commands

### Energy Queries
- **"How much energy am I using today"**
- **"What's my current power consumption"**
- **"Energy usage this week"**
- **"Energy cost today"**
- **"Power consumption now"**

## Usage Examples

### Record Energy Reading
```bash
curl -X POST http://localhost:8000/api/v1/energy/readings \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "light_001",
    "power_watts": 60.5,
    "device_name": "Living Room Light"
  }'
```

### Get Current Power
```bash
curl http://localhost:8000/api/v1/energy/current
```

### Get Daily Summary
```bash
curl http://localhost:8000/api/v1/energy/summary
```

### Get Energy Insights
```bash
curl http://localhost:8000/api/v1/energy/insights?days=7
```

### Create Device Profile
```bash
curl -X POST http://localhost:8000/api/v1/energy/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "light_001",
    "device_name": "Living Room Light",
    "rated_power_watts": 60,
    "typical_power_watts": 55,
    "standby_power_watts": 0.5,
    "cost_per_kwh": 0.12
  }'
```

## Database Models

- **DeviceEnergyReading**: Individual energy readings
- **DeviceEnergyProfile**: Device energy profiles
- **EnergyAlert**: Energy consumption alerts
- **EnergySummary**: Daily energy summaries

## Energy Calculation

Energy consumption is calculated by integrating power over time:
- Energy (kWh) = ∫ Power (W) dt / 1000
- Cost = Energy (kWh) × Cost per kWh

## Architecture

```
Energy Monitoring System
├── EnergyMonitor
│   ├── Reading recording
│   ├── Consumption calculation
│   ├── Summary generation
│   ├── Insights analysis
│   └── Alert management
└── EnergyTool (Voice)
    ├── Energy queries
    └── Natural language parsing
```

## Testing

Run the test script:
```bash
python3 test_energy_monitoring.py
```

## Status

✅ **Fully Functional**
- Energy tracking: ✅ Working
- Cost calculation: ✅ Working
- Daily summaries: ✅ Working
- Energy insights: ✅ Working
- Voice commands: ✅ Working (11 tools registered)
- Energy alerts: ✅ Working

## Future Enhancements

- Real-time device integration
- Smart meter integration
- Energy usage predictions
- Energy efficiency recommendations
- Carbon footprint tracking
- Time-of-use pricing
- Energy goal setting
- Automated energy optimization
- Integration with utility APIs
- Energy reports and exports

