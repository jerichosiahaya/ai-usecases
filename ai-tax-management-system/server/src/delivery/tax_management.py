from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from loguru import logger
from src.domain.http_response import ok, internal_server_error, bad_request_error, Response
from src.config.dependencies import TaxManagementDep

router = APIRouter(prefix="/api/v1/tax", tags=["tax-management"])

@router.get("/gl-transactions")
async def get_all_gl_transactions(
    urn: Optional[str] = None,
    tax_management_service: TaxManagementDep = None
):
    try:
        
        result = tax_management_service.get_gl_transactions(urn=urn)

        logger.info(f"Retrieved {len(result)} G/L transactions")

        response_content = Response(
            status="Success",
            message="G/L transactions retrieved successfully",
            data=[item.model_dump(by_alias=True) for item in result]
        )

        return JSONResponse(content=response_content.model_dump(), status_code=200)
    
    except Exception as e:
        logger.error(f"Error retrieving G/L transactions: {e}")
        return JSONResponse(content=response_content.model_dump(), status_code=500)
    
@router.get("/tax-invoices")
async def get_all_tax_invoices(
    urn: Optional[str] = None,
    tax_management_service: TaxManagementDep = None
):
    try:
        
        result = tax_management_service.get_tax_invoices(urn=urn)

        logger.info(f"Retrieved {len(result)} tax invoices")

        response_content = Response(
            status="Success",
            message="Tax invoices retrieved successfully",
            data=[item.model_dump(by_alias=True) for item in result]
        )

        return JSONResponse(content=response_content.model_dump(), status_code=200)
    
    except Exception as e:
        logger.error(f"Error retrieving tax invoices: {e}")
        return JSONResponse(content=response_content.model_dump(), status_code=500)
    
@router.get("/invoices")
async def get_all_invoices(
    urn: Optional[str] = None,
    tax_management_service: TaxManagementDep = None
):
    try:
        
        result = tax_management_service.get_invoices(urn=urn)

        logger.info(f"Retrieved {len(result)} invoices")

        response_content = Response(
            status="Success",
            message="Invoices retrieved successfully",
            data=[item.model_dump(by_alias=True) for item in result]
        )

        return JSONResponse(content=response_content.model_dump(), status_code=200)
    
    except Exception as e:
        logger.error(f"Error retrieving invoices: {e}")
        return JSONResponse(content=response_content.model_dump(), status_code=500)