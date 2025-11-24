"""Distributed tracing support"""

import uuid
import time
from typing import Dict, Optional, List
from datetime import datetime
from threading import local
from collections import deque
import json
from pathlib import Path
from home_assistant_platform.config.settings import settings


class Span:
    """Represents a single span in a trace"""
    
    def __init__(self, trace_id: str, span_id: str, name: str, parent_id: Optional[str] = None):
        self.trace_id = trace_id
        self.span_id = span_id
        self.name = name
        self.parent_id = parent_id
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.tags: Dict[str, str] = {}
        self.logs: List[Dict] = []
        self.status = "started"
    
    def finish(self, status: str = "ok"):
        """Finish the span"""
        self.end_time = time.time()
        self.status = status
    
    def add_tag(self, key: str, value: str):
        """Add a tag to the span"""
        self.tags[key] = value
    
    def add_log(self, message: str, level: str = "info", **kwargs):
        """Add a log entry to the span"""
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "level": level,
            **kwargs
        })
    
    def duration(self) -> float:
        """Get span duration in seconds"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def to_dict(self) -> Dict:
        """Convert span to dictionary"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "name": self.name,
            "parent_id": self.parent_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration(),
            "tags": self.tags,
            "logs": self.logs,
            "status": self.status
        }


class Tracer:
    """Distributed tracer"""
    
    def __init__(self, max_traces: int = 1000):
        self.traces: Dict[str, List[Span]] = {}
        self.spans: Dict[str, Span] = {}
        self.max_traces = max_traces
        self.traces_file = settings.data_dir / "traces" / "traces.json"
        self.traces_file.parent.mkdir(parents=True, exist_ok=True)
        self._local = local()
    
    def start_span(self, name: str, parent_span: Optional[Span] = None, tags: Optional[Dict[str, str]] = None) -> Span:
        """Start a new span"""
        # Get or create trace ID
        if not hasattr(self._local, 'trace_id'):
            self._local.trace_id = str(uuid.uuid4())
        
        trace_id = self._local.trace_id
        span_id = str(uuid.uuid4())
        parent_id = parent_span.span_id if parent_span else None
        
        span = Span(trace_id, span_id, name, parent_id)
        
        if tags:
            for key, value in tags.items():
                span.add_tag(key, str(value))
        
        # Store span
        self.spans[span_id] = span
        
        # Add to trace
        if trace_id not in self.traces:
            self.traces[trace_id] = []
        self.traces[trace_id].append(span)
        
        # Limit trace size
        if len(self.traces) > self.max_traces:
            # Remove oldest trace
            oldest_trace = min(self.traces.keys(), key=lambda k: min(s.start_time for s in self.traces[k]))
            del self.traces[oldest_trace]
        
        return span
    
    def finish_span(self, span: Span, status: str = "ok"):
        """Finish a span"""
        span.finish(status)
    
    def get_trace(self, trace_id: str) -> Optional[List[Dict]]:
        """Get a trace by ID"""
        if trace_id in self.traces:
            return [span.to_dict() for span in self.traces[trace_id]]
        return None
    
    def get_traces(self, limit: int = 100) -> List[Dict]:
        """Get recent traces"""
        all_traces = []
        for trace_id, spans in list(self.traces.items())[-limit:]:
            all_traces.append({
                "trace_id": trace_id,
                "spans": [span.to_dict() for span in spans],
                "start_time": min(s.start_time for s in spans),
                "duration": max(s.end_time or time.time() for s in spans) - min(s.start_time for s in spans)
            })
        return sorted(all_traces, key=lambda t: t["start_time"], reverse=True)
    
    def save_traces(self):
        """Save traces to file"""
        try:
            with open(self.traces_file, 'w') as f:
                json.dump(self.get_traces(limit=100), f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving traces: {e}")


# Global tracer instance
_tracer: Optional[Tracer] = None


def get_tracer() -> Tracer:
    """Get the global tracer"""
    global _tracer
    if _tracer is None:
        _tracer = Tracer()
    return _tracer



