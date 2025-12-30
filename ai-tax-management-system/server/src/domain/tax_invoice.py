from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


class TaxInvoiceDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    tax_invoice_detail_id: str = Field(..., alias="taxInvoiceDetailId", description="Primary key of tax invoice detail")
    item_code: str = Field(..., alias="itemCode", description="Item/product code")
    item_name: str = Field(..., alias="itemName", description="Item/product name")
    price: float = Field(..., ge=0, description="Unit price")
    quantity: float = Field(..., ge=0, description="Quantity of items")
    tax_base_wht: float = Field(..., alias="taxBaseWht", ge=0, description="Tax base for withholding tax")

class TaxInvoice(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    tax_invoice_id: str = Field(..., alias="taxInvoiceId", description="Primary key of tax invoice")
    urn: str = Field(..., description="Unique reference number")
    tax_invoice_number: str = Field(..., alias="taxInvoiceNumber", description="Tax invoice number or code")
    invoice_number: str = Field(..., alias="invoiceNumber", description="Invoice number or code")
    tax_invoice_date: str = Field(..., alias="taxInvoiceDate", description="Date of tax invoice (ISO format: YYYY-MM-DD)")
    nama_pengusaha_kena_pajak: str = Field(..., alias="namaPengusahaKenaPajak", description="Nama Pengusaha Kena Pajak (Seller name)")
    alamat_pengusaha_kena_pajak: str = Field(..., alias="alamatPengusahaKenaPajak", description="Alamat Pengusaha Kena Pajak (Seller address)")
    npwp_pengusaha_kena_pajak: str = Field(..., alias="npwpPengusahaKenaPajak", description="NPWP Pengusaha Kena Pajak (seller tax ID)")
    nama_pembeli_kena_pajak: str = Field(..., alias="namaPembeliKenaPajak", description="Nama Pembeli Kena Pajak (Buyer name)")
    alamat_pembeli_kena_pajak: str = Field(..., alias="alamatPembeliKenaPajak", description="Alamat Pembeli Kena Pajak (Buyer address)")
    npwp_pembeli_kena_pajak: Optional[str] = Field(None, alias="npwpPembeliKenaPajak", description="NPWP Pembeli Kena Pajak (buyer tax ID, optional if using other ID)")
    nik_pembeli_kena_pajak: Optional[str] = Field(None, alias="nikPembeliKenaPajak", description="NIK Pembeli Kena Pajak (national ID)")
    nomer_paspor_pembeli_kena_pajak: Optional[str] = Field(None, alias="nomorPasporPembeliKenaPajak", description="Nomor Paspor Pembeli Kena Pajak (Passport number)")
    email_pembeli_kena_pajak: str = Field(..., alias="emailPembeliKenaPajak", description="Email Pembeli Kena Pajak (Buyer email)")
    tax_invoice_detail: List[TaxInvoiceDetail] = Field(..., alias="taxInvoiceDetail", min_length=1, description="List of tax invoice detail line items")
    total_tax_base_wht: float = Field(..., alias="totalTaxBaseWht", ge=0, description="Total Harga Jual / Penggantian / Uang Muka / Termin (Total tax base)")
    dikurangi_potongan_harga: float = Field(default=0.0, alias="dikurangiPotonganHarga", ge=0, description="Dikurangi potongan harga (Less: price discount)")
    dikurangi_uang_muka_yang_telah_diterima: float = Field(default=0.0, alias="dikurangiUangMukaYangTelahDiterima", ge=0, description="Dikurangi uang muka yang telah diterima (Less: advance payment received)")
    dasar_pengenaan_pajak: float = Field(..., alias="dasarPengenaanPajak", ge=0, description="Dasar Pengenaan Pajak (Tax base)")
    jumlah_ppn: float = Field(default=0.0, alias="jumlahPpn", ge=0, description="Jumlah PPN (Total PPN/VAT)")
    jumlah_ppnbm: float = Field(default=0.0, alias="jumlahPpnbm", ge=0, description="Jumlah PPnBM (Total PPNBM/Luxury Tax)")
    created_at: str = Field(..., alias="createdAt", description="ISO timestamp when tax invoice was created")
    updated_at: str = Field(..., alias="updatedAt", description="ISO timestamp when tax invoice was last updated")
