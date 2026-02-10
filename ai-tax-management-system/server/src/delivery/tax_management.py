from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from loguru import logger
from src.domain.http_response import ok, internal_server_error, bad_request_error, Response
from src.config.dependencies import TaxManagementDep

router = APIRouter(prefix="/api/v1/tax", tags=["tax-management"])

@router.get("/gl-transactions")
async def get_all_gl_transactions(
    urn: Optional[str] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    tax_management_service: TaxManagementDep = None
):
    try:
        result, total = tax_management_service.get_gl_transactions(
            urn=urn,
            page=page,
            page_size=page_size
        )

        logger.info(f"Retrieved {len(result)} G/L transactions (page {page} of {(total + page_size - 1) // page_size})")

        response_content = Response(
            status="Success",
            message="G/L transactions retrieved successfully",
            data={
                "items": [item.model_dump(by_alias=True) for item in result],
                "total": total,
                "page": page,
                "pageSize": page_size,
                "totalPages": (total + page_size - 1) // page_size
            }
        )

        return JSONResponse(content=response_content.model_dump(), status_code=200)
    
    except Exception as e:
        logger.error(f"Error retrieving G/L transactions: {e}")
        error_response = Response(
            status="Error",
            message=str(e),
            data=None
        )
        return JSONResponse(content=error_response.model_dump(), status_code=500)

@router.get("/gl-transactions/{urn}")
async def get_gl_transaction_by_urn(
    urn: str,
    tax_management_service: TaxManagementDep = None
):
    try:
        result = tax_management_service.get_gl_transaction_by_urn(urn=urn)
        
        if not result:
            error_response = Response(
                status="Error",
                message=f"GL transaction with URN {urn} not found",
                data=None
            )
            return JSONResponse(content=error_response.model_dump(), status_code=404)

        logger.info(f"Retrieved G/L transaction: {urn}")

        response_content = Response(
            status="Success",
            message="G/L transaction retrieved successfully",
            data=result.model_dump(by_alias=True)
        )

        return JSONResponse(content=response_content.model_dump(), status_code=200)
    
    except Exception as e:
        logger.error(f"Error retrieving G/L transaction {urn}: {e}")
        error_response = Response(
            status="Error",
            message=str(e),
            data=None
        )
        return JSONResponse(content=error_response.model_dump(), status_code=500)
    
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

@router.get("/dashboard-stats")
async def get_dashboard_stats(
    tax_management_service: TaxManagementDep = None
):
    try:
        result = tax_management_service.get_dashboard_stats()
        
        logger.info(f"Retrieved dashboard stats: {result}")
        
        response_content = Response(
            status="Success",
            message="Dashboard stats retrieved successfully",
            data=result
        )
        
        return JSONResponse(content=response_content.model_dump(), status_code=200)
    except Exception as e:
        logger.error(f"Error retrieving dashboard stats: {e}")
        error_response = Response(
            status="Error",
            message=str(e),
            data=None
        )
        return JSONResponse(content=error_response.model_dump(), status_code=500)