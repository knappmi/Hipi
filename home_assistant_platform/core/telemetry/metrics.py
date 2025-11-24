"""Metrics collection for monitoring platform performance"""

import time
from typing import Dict, Optional, Callable
from collections import defaultdict, deque
from threading import Lock
from datetime import datetime, timedelta
import json
from pathlib import Path
from home_assistant_platform.config.settings import settings


class Metric:
    """Represents a single metric"""
    
    def __init__(self, name: str, value: float, tags: Optional[Dict[str, str]] = None, timestamp: Optional[datetime] = None):
        self.name = name
        self.value = value
        self.tags = tags or {}
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert metric to dictionary"""
        return {
            "name": self.name,
            "value": self.value,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat()
        }


class MetricsCollector:
    """Collects and stores metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.metrics: deque = deque(maxlen=max_history)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
        self.metrics_file = settings.data_dir / "metrics" / "metrics.json"
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        with self.lock:
            key = self._make_key(name, tags)
            self.counters[key] += value
            self._record_metric(name, float(self.counters[key]), tags, "counter")
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        with self.lock:
            key = self._make_key(name, tags)
            self.gauges[key] = value
            self._record_metric(name, value, tags, "gauge")
    
    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram value"""
        with self.lock:
            key = self._make_key(name, tags)
            self.histograms[key].append(value)
            # Keep only last 100 values per histogram
            if len(self.histograms[key]) > 100:
                self.histograms[key] = self.histograms[key][-100:]
            self._record_metric(name, value, tags, "histogram")
    
    def timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations"""
        return Timer(self, name, tags)
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a unique key for a metric"""
        if tags:
            tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
            return f"{name}:{tag_str}"
        return name
    
    def _record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]], metric_type: str):
        """Record a metric"""
        metric = Metric(name, value, tags)
        metric.tags["type"] = metric_type
        self.metrics.append(metric)
    
    def get_metrics(self, name: Optional[str] = None, tags: Optional[Dict[str, str]] = None, 
                   since: Optional[datetime] = None) -> list:
        """Get metrics matching criteria"""
        with self.lock:
            results = []
            for metric in self.metrics:
                if name and metric.name != name:
                    continue
                if tags and not all(metric.tags.get(k) == v for k, v in tags.items()):
                    continue
                if since and metric.timestamp < since:
                    continue
                results.append(metric.to_dict())
            return results
    
    def get_summary(self) -> Dict:
        """Get summary of all metrics"""
        with self.lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histogram_counts": {k: len(v) for k, v in self.histograms.items()},
                "total_metrics": len(self.metrics),
                "latest_metrics": [m.to_dict() for m in list(self.metrics)[-10:]]
            }
    
    def save_metrics(self):
        """Save metrics to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.get_summary(), f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving metrics: {e}")


class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, collector: MetricsCollector, name: str, tags: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.name = name
        self.tags = tags
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.collector.histogram(f"{self.name}.duration", duration, self.tags)
        self.collector.gauge(f"{self.name}.last_duration", duration, self.tags)


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector



