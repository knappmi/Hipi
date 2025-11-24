# Plugin Telemetry Guide

This guide explains how plugins can instrument their own telemetry (logs, metrics, and tracing) that integrates with the platform's telemetry system.

## Overview

The platform provides a comprehensive telemetry system that plugins can use to:
- **Logging**: Structured logging with context
- **Metrics**: Counters, gauges, and histograms
- **Tracing**: Distributed tracing for request flows

## Logging

### Basic Logging

Plugins can use Python's standard logging module, which is automatically configured by the platform:

```python
import logging

logger = logging.getLogger(__name__)

def handle_command(command):
    logger.info(f"Processing command: {command}")
    try:
        result = process_command(command)
        logger.info(f"Command processed successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing command: {e}", exc_info=True)
        raise
```

### Structured Logging

For structured logging with additional context:

```python
import logging

logger = logging.getLogger(__name__)

def handle_command(command, user_id=None):
    # Add extra context
    extra = {
        "plugin_id": "my_plugin",
        "command": command,
        "user_id": user_id
    }
    logger.info("Processing command", extra={"extra_fields": extra})
```

## Metrics

### Using the Metrics API

Plugins can access the platform's metrics collector via the plugin API:

```python
import requests

def record_metric(metric_name, value, metric_type="gauge", tags=None):
    """Record a metric via the plugin API"""
    response = requests.post(
        "http://platform:8000/api/v1/telemetry/metrics",
        json={
            "name": f"plugin.my_plugin.{metric_name}",
            "value": value,
            "type": metric_type,
            "tags": tags or {}
        }
    )
    return response.json()
```

### Metric Types

1. **Counter**: Increment a counter
```python
record_metric("commands_processed", 1, "counter", {"status": "success"})
```

2. **Gauge**: Set a current value
```python
record_metric("active_connections", 5, "gauge")
```

3. **Histogram**: Record a distribution
```python
record_metric("response_time", 0.234, "histogram")
```

### Example: Instrumenting a Plugin

```python
import time
import requests

class MyPlugin:
    def __init__(self):
        self.api_base = "http://platform:8000/api/v1"
    
    def process_request(self, request_data):
        start_time = time.time()
        
        # Record request received
        self._record_metric("requests_received", 1, "counter")
        
        try:
            result = self._do_work(request_data)
            
            # Record success
            duration = time.time() - start_time
            self._record_metric("requests_success", 1, "counter")
            self._record_metric("request_duration", duration, "histogram")
            
            return result
        except Exception as e:
            # Record error
            self._record_metric("requests_error", 1, "counter", {"error_type": type(e).__name__})
            raise
    
    def _record_metric(self, name, value, metric_type, tags=None):
        try:
            requests.post(
                f"{self.api_base}/telemetry/metrics",
                json={
                    "name": f"plugin.my_plugin.{name}",
                    "value": value,
                    "type": metric_type,
                    "tags": tags or {}
                },
                timeout=1
            )
        except:
            pass  # Don't fail if metrics can't be sent
```

## Tracing

### Creating Spans

Plugins can create spans for distributed tracing:

```python
import requests

def create_span(span_name, parent_trace_id=None, tags=None):
    """Create a trace span via the plugin API"""
    response = requests.post(
        "http://platform:8000/api/v1/telemetry/traces/spans",
        json={
            "name": span_name,
            "parent_trace_id": parent_trace_id,
            "tags": tags or {}
        }
    )
    return response.json()

def finish_span(span_id, status="ok"):
    """Finish a span"""
    requests.post(
        f"http://platform:8000/api/v1/telemetry/traces/spans/{span_id}/finish",
        json={"status": status}
    )
```

### Example: Tracing a Plugin Operation

```python
import requests

class MyPlugin:
    def __init__(self):
        self.api_base = "http://platform:8000/api/v1"
        self.current_span_id = None
    
    def process_request(self, request_data, trace_id=None):
        # Start span
        span = self._start_span("plugin.process_request", trace_id)
        
        try:
            # Add tags
            self._add_span_tag(span["span_id"], "plugin_id", "my_plugin")
            self._add_span_tag(span["span_id"], "request_type", request_data.get("type"))
            
            # Do work
            result = self._do_work(request_data)
            
            # Finish span successfully
            self._finish_span(span["span_id"], "ok")
            return result
        except Exception as e:
            # Finish span with error
            self._add_span_log(span["span_id"], f"Error: {str(e)}", "error")
            self._finish_span(span["span_id"], "error")
            raise
    
    def _start_span(self, name, parent_trace_id):
        response = requests.post(
            f"{self.api_base}/telemetry/traces/spans",
            json={
                "name": name,
                "parent_trace_id": parent_trace_id,
                "tags": {}
            }
        )
        return response.json()
    
    def _add_span_tag(self, span_id, key, value):
        requests.post(
            f"{self.api_base}/telemetry/traces/spans/{span_id}/tags",
            json={key: str(value)}
        )
    
    def _add_span_log(self, span_id, message, level="info"):
        requests.post(
            f"{self.api_base}/telemetry/traces/spans/{span_id}/logs",
            json={"message": message, "level": level}
        )
    
    def _finish_span(self, span_id, status):
        requests.post(
            f"{self.api_base}/telemetry/traces/spans/{span_id}/finish",
            json={"status": status}
        )
```

## Best Practices

1. **Use Consistent Naming**: Prefix all plugin metrics with `plugin.<plugin_id>`
2. **Add Context**: Include relevant tags (plugin_id, operation_type, etc.)
3. **Don't Block**: Telemetry calls should be non-blocking and not fail the main operation
4. **Use Appropriate Levels**: 
   - DEBUG: Detailed diagnostic information
   - INFO: General informational messages
   - WARNING: Warning messages for potential issues
   - ERROR: Error messages for failures
5. **Record Timing**: Use histograms for timing metrics (response times, durations)
6. **Track Errors**: Always record error metrics with error types as tags

## Accessing Telemetry Data

Plugins can query their own telemetry data:

```python
# Get metrics
response = requests.get(
    "http://platform:8000/api/v1/telemetry/metrics",
    params={"name": "plugin.my_plugin.*"}
)

# Get traces
response = requests.get(
    "http://platform:8000/api/v1/telemetry/traces",
    params={"plugin_id": "my_plugin", "limit": 10}
)
```

## Integration with Platform

The platform automatically:
- Collects logs from plugin containers
- Aggregates metrics from all plugins
- Correlates traces across plugins and platform
- Provides dashboards for viewing telemetry data

## Example: Complete Plugin with Telemetry

```python
import logging
import time
import requests

logger = logging.getLogger(__name__)

class InstrumentedPlugin:
    def __init__(self, plugin_id):
        self.plugin_id = plugin_id
        self.api_base = "http://platform:8000/api/v1"
    
    def handle_command(self, command, trace_id=None):
        start_time = time.time()
        span_id = None
        
        try:
            # Start trace span
            if trace_id:
                span = self._start_span("plugin.handle_command", trace_id)
                span_id = span["span_id"]
                self._add_span_tag(span_id, "command", command)
            
            logger.info(f"Processing command: {command}", extra={
                "extra_fields": {
                    "plugin_id": self.plugin_id,
                    "command": command
                }
            })
            
            # Record metric
            self._record_metric("commands_received", 1, "counter")
            
            # Process command
            result = self._process(command)
            
            # Record success metrics
            duration = time.time() - start_time
            self._record_metric("commands_success", 1, "counter")
            self._record_metric("command_duration", duration, "histogram")
            
            logger.info(f"Command processed successfully", extra={
                "extra_fields": {
                    "plugin_id": self.plugin_id,
                    "command": command,
                    "duration": duration
                }
            })
            
            # Finish span
            if span_id:
                self._finish_span(span_id, "ok")
            
            return result
            
        except Exception as e:
            # Record error metrics
            self._record_metric("commands_error", 1, "counter", {
                "error_type": type(e).__name__
            })
            
            logger.error(f"Error processing command: {e}", exc_info=True, extra={
                "extra_fields": {
                    "plugin_id": self.plugin_id,
                    "command": command
                }
            })
            
            # Finish span with error
            if span_id:
                self._add_span_log(span_id, str(e), "error")
                self._finish_span(span_id, "error")
            
            raise
    
    def _process(self, command):
        # Your plugin logic here
        return {"result": "success"}
    
    def _record_metric(self, name, value, metric_type, tags=None):
        try:
            requests.post(
                f"{self.api_base}/telemetry/metrics",
                json={
                    "name": f"plugin.{self.plugin_id}.{name}",
                    "value": value,
                    "type": metric_type,
                    "tags": tags or {}
                },
                timeout=0.5
            )
        except:
            pass
    
    def _start_span(self, name, parent_trace_id):
        try:
            response = requests.post(
                f"{self.api_base}/telemetry/traces/spans",
                json={
                    "name": name,
                    "parent_trace_id": parent_trace_id,
                    "tags": {"plugin_id": self.plugin_id}
                },
                timeout=0.5
            )
            return response.json()
        except:
            return {"span_id": None}
    
    def _add_span_tag(self, span_id, key, value):
        if not span_id:
            return
        try:
            requests.post(
                f"{self.api_base}/telemetry/traces/spans/{span_id}/tags",
                json={key: str(value)},
                timeout=0.5
            )
        except:
            pass
    
    def _add_span_log(self, span_id, message, level):
        if not span_id:
            return
        try:
            requests.post(
                f"{self.api_base}/telemetry/traces/spans/{span_id}/logs",
                json={"message": message, "level": level},
                timeout=0.5
            )
        except:
            pass
    
    def _finish_span(self, span_id, status):
        if not span_id:
            return
        try:
            requests.post(
                f"{self.api_base}/telemetry/traces/spans/{span_id}/finish",
                json={"status": status},
                timeout=0.5
            )
        except:
            pass
```

## Summary

Plugins can fully integrate with the platform's telemetry system by:
1. Using standard Python logging (automatically collected)
2. Sending metrics via the telemetry API
3. Creating and managing trace spans
4. Following best practices for naming and context

All telemetry data is automatically aggregated and available through the platform's monitoring dashboards.



