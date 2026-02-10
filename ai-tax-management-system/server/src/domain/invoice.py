from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List

class InvoiceDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    invoice_detail_id: str = Field(..., alias="invoiceDetailId", description="Primary key of invoice detail")
    item_name: str = Field(..., alias="itemName", description="Name of the item/service")
    quantity: float = Field(..., ge=0, description="Quantity of items")
    unit_price: float = Field(..., alias="unitPrice", ge=0, description="Unit price per item")
    tax_percentage: float = Field(..., alias="taxPercentage", ge=0, le=100, description="Tax percentage (0-100)")
    discount_percentage: float = Field(..., alias="discountPercentage", ge=0, le=100, description="Discount percentage (0-100)")
    extended_price: float = Field(..., alias="extendedPrice", description="Calculated amount after tax and discount")

class Invoice(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    invoice_id: str = Field(..., alias="invoiceId", description="Primary key of invoice")
    invoice_number: str = Field(..., alias="invoiceNumber", description="Invoice number")
    urn: str = Field(..., description="Unique Reference Number")
    document_url: Optional[str] = Field(None, alias="documentUrl", description="Azure Blob Storage URL for document preview")
    project_number: str = Field(..., alias="projectNumber", description="Project number reference")
    invoice_detail: List[InvoiceDetail] = Field(..., alias="invoiceDetail", min_length=1, description="List of invoice detail line items")
    sub_total_amount: float = Field(..., alias="subTotalAmount", ge=0, description="Subtotal amount before tax")
    vat_percentage: Optional[float] = Field(None, alias="vatPercentage", ge=0, le=100, description="VAT percentage (0-100)")
    vat_amount: float = Field(..., alias="vatAmount", ge=0, description="VAT amount")
    discount_amount: Optional[float] = Field(default=0.0, alias="discountAmount", ge=0, description="Total discount amount")
    wht_percentage: Optional[float] = Field(None, alias="whtPercentage", ge=0, le=100, description="Withholding tax percentage (0-100)")
    wht_amount: Optional[float] = Field(None, alias="whtAmount", description="Withholding tax amount")
    total_amount: float = Field(..., alias="totalAmount", description="Final total invoice amount")
    currency: str = Field(..., pattern="^[A-Z]{3}$", description="Currency code (ISO 4217 - e.g., USD, IDR, SGD)")
    created_at: str = Field(..., alias="createdAt", description="ISO timestamp when invoice was created")
    updated_at: str = Field(..., alias="updatedAt", description="ISO timestamp when invoice was last updated")