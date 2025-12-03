"""Advanced automation API endpoints"""

import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

router = APIRouter()


class ScriptExecute(BaseModel):
    language: str  # "python" or "javascript"
    script: str
    context: Optional[Dict[str, Any]] = None


@router.post("/automation/scripts/execute")
async def execute_script(request: Request, script_data: ScriptExecute):
    """Execute a Python or JavaScript script"""
    script_executor = request.app.state.script_executor
    
    if script_data.language == "python":
        result = script_executor.execute_python_script(
            script_data.script,
            script_data.context or {}
        )
    elif script_data.language == "javascript":
        result = script_executor.execute_javascript_script(
            script_data.script,
            script_data.context or {}
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {script_data.language}")
    
    return result

