"""Script executor for advanced automation scripting"""

import logging
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ScriptExecutor:
    """Executes Python and JavaScript scripts for automations"""
    
    def __init__(self, scripts_dir: Optional[Path] = None):
        self.scripts_dir = scripts_dir or Path(tempfile.gettempdir()) / "automation_scripts"
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
    
    def execute_python_script(
        self,
        script_code: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a Python script with context"""
        # Create temporary script file
        script_file = self.scripts_dir / f"script_{id(script_code)}.py"
        
        try:
            # Write script with context injection
            script_content = self._wrap_python_script(script_code, context)
            script_file.write_text(script_content)
            
            # Execute script
            result = subprocess.run(
                ["python3", str(script_file)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.scripts_dir)
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr,
                    "output": result.stdout
                }
            
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Script execution timeout (30s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # Cleanup
            if script_file.exists():
                script_file.unlink()
    
    def execute_javascript_script(
        self,
        script_code: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a JavaScript script with context"""
        # Check if node is available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {
                "success": False,
                "error": "Node.js is not installed"
            }
        
        # Create temporary script file
        script_file = self.scripts_dir / f"script_{id(script_code)}.js"
        
        try:
            # Write script with context injection
            script_content = self._wrap_javascript_script(script_code, context)
            script_file.write_text(script_content)
            
            # Execute script
            result = subprocess.run(
                ["node", str(script_file)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.scripts_dir)
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr,
                    "output": result.stdout
                }
            
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Script execution timeout (30s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # Cleanup
            if script_file.exists():
                script_file.unlink()
    
    def _wrap_python_script(self, script_code: str, context: Dict[str, Any]) -> str:
        """Wrap Python script with context"""
        context_str = "\n".join([f"{k} = {repr(v)}" for k, v in context.items()])
        return f"""
# Context variables
{context_str}

# User script
{script_code}
"""
    
    def _wrap_javascript_script(self, script_code: str, context: Dict[str, Any]) -> str:
        """Wrap JavaScript script with context"""
        import json
        context_str = json.dumps(context, indent=2)
        return f"""
// Context variables
const context = {context_str};
const {{ {', '.join(context.keys())} }} = context;

// User script
{script_code}
"""

