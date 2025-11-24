"""Telemetry API endpoints for metrics and tracing"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import logging

from home_assistant_platform.core.telemetry.metrics import get_metrics
from home_assistant_platform.core.telemetry.tracing import get_tracer

logger = logging.getLogger(__name__)
router = APIRouter()


class MetricRequest(BaseModel):
    name: str
    value: float
    type: str  # counter, gauge, histogram
    tags: Optional[Dict[str, str]] = None


class SpanRequest(BaseModel):
    name: str
    parent_trace_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


@router.post("/metrics")
async def record_metric(request: Request, metric_req: MetricRequest):
    """Record a metric"""
    try:
        metrics = get_metrics()
        
        if metric_req.type == "counter":
            metrics.increment(metric_req.name, int(metric_req.value), metric_req.tags)
        elif metric_req.type == "gauge":
            metrics.gauge(metric_req.name, metric_req.value, metric_req.tags)
        elif metric_req.type == "histogram":
            metrics.histogram(metric_req.name, metric_req.value, metric_req.tags)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown metric type: {metric_req.type}")
        
        return {"success": True, "message": "Metric recorded"}
    except Exception as e:
        logger.error(f"Error recording metric: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics_endpoint(request: Request, name: Optional[str] = None, 
                               limit: int = 100):
    """Get metrics"""
    try:
        metrics = get_metrics()
        
        if name:
            metric_data = metrics.get_metrics(name=name)
        else:
            metric_data = metrics.get_summary()
        
        return {"metrics": metric_data}
    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/traces/spans")
async def create_span(request: Request, span_req: SpanRequest):
    """Create a new trace span"""
    try:
        tracer = get_tracer()
        span = tracer.start_span(span_req.name, tags=span_req.tags)
        
        return {
            "success": True,
            "trace_id": span.trace_id,
            "span_id": span.span_id
        }
    except Exception as e:
        logger.error(f"Error creating span: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/traces/spans/{span_id}/finish")
async def finish_span(request: Request, span_id: str, status: str = "ok"):
    """Finish a span"""
    try:
        tracer = get_tracer()
        if span_id not in tracer.spans:
            raise HTTPException(status_code=404, detail="Span not found")
        
        span = tracer.spans[span_id]
        tracer.finish_span(span, status)
        
        return {"success": True, "message": "Span finished"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finishing span: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/traces/spans/{span_id}/tags")
async def add_span_tag(request: Request, span_id: str, tags: Dict[str, str]):
    """Add tags to a span"""
    try:
        tracer = get_tracer()
        if span_id not in tracer.spans:
            raise HTTPException(status_code=404, detail="Span not found")
        
        span = tracer.spans[span_id]
        for key, value in tags.items():
            span.add_tag(key, value)
        
        return {"success": True, "message": "Tags added"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding span tags: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/traces/spans/{span_id}/logs")
async def add_span_log(request: Request, span_id: str, message: str, level: str = "info"):
    """Add a log entry to a span"""
    try:
        tracer = get_tracer()
        if span_id not in tracer.spans:
            raise HTTPException(status_code=404, detail="Span not found")
        
        span = tracer.spans[span_id]
        span.add_log(message, level)
        
        return {"success": True, "message": "Log added"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding span log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces")
async def get_traces(request: Request, limit: int = 100):
    """Get recent traces"""
    try:
        tracer = get_tracer()
        traces = tracer.get_traces(limit=limit)
        return {"traces": traces}
    except Exception as e:
        logger.error(f"Error getting traces: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces/{trace_id}")
async def get_trace(request: Request, trace_id: str):
    """Get a specific trace"""
    try:
        tracer = get_tracer()
        trace = tracer.get_trace(trace_id)
        if trace is None:
            raise HTTPException(status_code=404, detail="Trace not found")
        return {"trace": trace}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trace: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



