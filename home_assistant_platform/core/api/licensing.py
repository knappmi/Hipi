"""Licensing API endpoints"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

router = APIRouter()


class LicenseRequest(BaseModel):
    license_key: str


@router.get("")
async def get_license_info(request: Request):
    """Get current license information"""
    validator = request.app.state.license_validator
    return {
        "tier": validator.get_license_tier(),
        "hardware_id": validator.hardware_id,
        "valid": validator.validate_license()
    }


@router.post("")
async def set_license(request: Request, license_req: LicenseRequest):
    """Set or update license"""
    validator = request.app.state.license_validator
    success = validator.set_license(license_req.license_key)
    
    if not success:
        raise HTTPException(status_code=400, detail="Invalid license key")
    
    return {
        "success": True,
        "tier": validator.get_license_tier(),
        "message": "License updated successfully"
    }


@router.get("/features/{feature}")
async def check_feature(request: Request, feature: str):
    """Check if license includes a feature"""
    validator = request.app.state.license_validator
    has_feature = validator.has_feature(feature)
    return {
        "feature": feature,
        "available": has_feature
    }

