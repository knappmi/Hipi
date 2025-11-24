"""Marketplace API endpoints"""

from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel

router = APIRouter()


def get_marketplace_registry(request: Request):
    """Get marketplace registry from app state"""
    if not hasattr(request.app.state, 'marketplace_registry'):
        from home_assistant_platform.marketplace.registry import MarketplaceRegistry
        request.app.state.marketplace_registry = MarketplaceRegistry()
    return request.app.state.marketplace_registry


def get_hardware_id(request: Request):
    """Get hardware ID for user identification"""
    from home_assistant_platform.core.licensing.hardware_id import get_or_create_hardware_id
    return get_or_create_hardware_id()


@router.get("/plugins")
async def list_marketplace_plugins(
    request: Request,
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_rating: Optional[float] = None,
    free_only: bool = False
):
    """List plugins in marketplace"""
    registry = get_marketplace_registry(request)
    plugins = registry.list_plugins(category, search, min_rating, free_only)
    return plugins


@router.get("/plugins/{plugin_id}")
async def get_marketplace_plugin(plugin_id: str, request: Request):
    """Get marketplace plugin details"""
    registry = get_marketplace_registry(request)
    plugin = registry.get_plugin(plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin


@router.post("/plugins/{plugin_id}/install")
async def install_marketplace_plugin(plugin_id: str, request: Request):
    """Install a plugin from marketplace"""
    registry = get_marketplace_registry(request)
    downloader = request.app.state.downloader if hasattr(request.app.state, 'downloader') else None
    
    if not downloader:
        from home_assistant_platform.marketplace.downloader import PluginDownloader
        downloader = PluginDownloader(registry)
        request.app.state.downloader = downloader
    
    user_id = get_hardware_id(request)
    
    # Download plugin
    zip_path = downloader.download_plugin(plugin_id, user_id)
    if not zip_path:
        raise HTTPException(status_code=400, detail="Failed to download plugin")
    
    # Validate package
    if not downloader.validate_plugin_package(zip_path):
        raise HTTPException(status_code=400, detail="Invalid plugin package")
    
    # Extract and install
    from pathlib import Path
    from home_assistant_platform.config.settings import settings
    import tempfile
    import shutil
    
    extract_dir = Path(tempfile.mkdtemp())
    if not downloader.extract_plugin(zip_path, extract_dir):
        raise HTTPException(status_code=400, detail="Failed to extract plugin")
    
    # Install plugin
    plugin_manager = request.app.state.plugin_manager if hasattr(request.app.state, 'plugin_manager') else None
    if not plugin_manager:
        from home_assistant_platform.core.plugin_manager.plugin_manager import PluginManager
        from home_assistant_platform.core.plugin_manager.docker_manager import DockerManager
        docker_manager = request.app.state.docker_manager
        plugin_manager = PluginManager(docker_manager)
        request.app.state.plugin_manager = plugin_manager
    
    success = plugin_manager.install_plugin(extract_dir)
    
    # Cleanup
    shutil.rmtree(extract_dir, ignore_errors=True)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to install plugin")
    
    return {"success": True, "message": f"Plugin {plugin_id} installed successfully"}


@router.post("/plugins/{plugin_id}/purchase")
async def purchase_plugin(plugin_id: str, request: Request, payment_data: Dict):
    """Purchase a plugin"""
    registry = get_marketplace_registry(request)
    user_id = get_hardware_id(request)
    
    if not hasattr(request.app.state, 'payment_processor'):
        from home_assistant_platform.marketplace.payment import PaymentProcessor
        request.app.state.payment_processor = PaymentProcessor(registry)
    
    payment_processor = request.app.state.payment_processor
    result = payment_processor.process_payment(
        plugin_id,
        user_id,
        payment_data.get("payment_method", "stripe"),
        payment_data
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Payment failed"))
    
    return result


@router.get("/purchases")
async def get_user_purchases(request: Request):
    """Get user's purchased plugins"""
    registry = get_marketplace_registry(request)
    user_id = get_hardware_id(request)
    purchases = registry.get_user_purchases(user_id)
    return purchases


@router.post("/plugins/{plugin_id}/review")
async def add_review(plugin_id: str, request: Request, review_data: Dict):
    """Add a review for a plugin"""
    registry = get_marketplace_registry(request)
    user_id = get_hardware_id(request)
    rating = review_data.get("rating")
    comment = review_data.get("comment")
    
    if not rating or rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    success = registry.add_review(plugin_id, user_id, rating, comment)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add review")
    
    return {"success": True, "message": "Review added"}

