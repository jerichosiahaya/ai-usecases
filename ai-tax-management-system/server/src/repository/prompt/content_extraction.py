def get_content_classification_prompt(document_content: str) -> str:
    return f"""
    You are an expert content classification AI specialized in categorizing financial documents such as invoices, tax invoices, and general ledgers. Your task is to analyze the provided document content and classify it into one of the predefined categories based on its content.

    When processing the document, consider the following guidelines:
    - Invoice: Documents that contain billing information, including vendor details, line items, totals, and payment terms.
    - Tax Invoice (Faktur Pajak): Documents that include tax-specific information, such as tax identification numbers, tax amounts, and regulatory compliance details.
    - General Ledger: Documents that provide a comprehensive record of all financial transactions, including debits and credits across various accounts.

    # General Instructions:
    - If the document lacks sufficient information to be classified into any of the above categories, classify it as "Unknown".
    - Assess whether the document appears to be complete based on the presence of key sections and information typically found in each document type.
    - Provide a confidence score (between 0 and 1) indicating your certainty about the classification.

    # CRITICAL: Tax Invoice (Faktur Pajak) Identification Rules
    
    ## Strong Tax Invoice Indicators (ANY of these should classify as Tax Invoice):
    - Explicit "Faktur Pajak" text in the document header
    - NPWP (Nomor Pokok Wajib Pajak) fields for both seller AND buyer
    - "Pengusaha Kena Pajak" or "PKP" terminology
    - "Pembeli Kena Pajak" or "BKP" terminology
    - Tax fields: "Dasar Pengenaan Pajak" (DPP), "Jumlah PPN", "Jumlah PPnBM"
    - Indonesian tax-specific terminology: "Dikurangi Potongan Harga", "Dikurangi Uang Muka"
    - Format matching Indonesian tax invoice structure with NPWP numbers (15-digit format)
    
    ## Multi-Page Tax Invoice Detection (for continuation pages WITHOUT header/NPWP):
    - **Table Column Headers**: Look for Indonesian tax-specific columns:
      * "Harga Jual/Penggantian/Uang Muka/Termin" or "Harga Jual" (selling price in tax context)
      * "Nama Barang Kena Pajak/Jasa Kena Pajak" (name of taxable goods/services)
      * "Kode Barang" or item codes in specific format
      * **"PPnBM" column** (Pajak Penjualan atas Barang Mewah - Luxury Tax)
      * **"Potongan Harga" column** (Price Discount)
    - **CRITICAL Tax Invoice Identifiers**:
      * Presence of BOTH "PPnBM" AND "Potongan Harga" columns is a DEFINITIVE indicator of Faktur Pajak
      * These columns are ALWAYS present in official Faktur Pajak but NOT in regular invoices
    - **Page Structure Indicators**:
      * Page appears truncated at top (starts mid-content, no header)
      * Sequential item numbering continuing from previous page (e.g., starts with item #15, #16...)
      * Table continues without introduction or document header
    - **Line Item Format**: 
      * Items listed in formal tax invoice table structure
      * Numeric item codes followed by descriptions and amounts
      * Consistent formatting matching official Faktur Pajak layout
    - **CRITICAL**: Even if NO "Faktur Pajak" text and NO NPWP visible, classify as Tax Invoice if table structure and column headers match Indonesian tax invoice format
    
    ## How to Differentiate Tax Invoice from Regular Invoice:
    - **Tax Invoice (Faktur Pajak)** indicators:
      * First page: Has NPWP, "Pengusaha Kena Pajak", "Faktur Pajak" header
      * Middle/continuation pages: Has tax-specific column headers ("Harga Jual/Penggantian"), formal table structure, sequential numbering
      * **DEFINITIVE INDICATOR**: Has BOTH "PPnBM" AND "Potongan Harga" columns in the line items table
      * Uses official Indonesian tax terminology and prescribed format
    - **Regular Invoice** indicators:
      * Generic column headers like "Description", "Amount", "Price", "Quantity"
      * May have VAT line at bottom, but table structure is informal/custom
      * Lacks official tax invoice column headers and terminology
      * **Does NOT have "PPnBM" or "Potongan Harga" columns**
    - **Decision Rule**: If table has "PPnBM" AND "Potongan Harga" columns → DEFINITELY Tax Invoice (even without NPWP or header)

    # Document Completeness Guidelines:

    ## Tax Invoice (Faktur Pajak) Completeness Indicators (document is COMPLETE when it has):
    - Digital signature or QR code indicating authorization
    - Name of city and date of issuance, e.g., "Jakarta, 15 Maret 2023"
    - Presence of signature note like: "Ditandatangani secara elektronik"
    - Page numbers indicating all pages are present, example: "2 dari 2"
    - Even though there is a notes that says something like "Ditandatangani secara elektronik", if there is no name of city and date of issuance or the person who signed, then consider the document as INCOMPLETE.

    # Completeness Assessment Logic:
    - Document is INCOMPLETE if it ends abruptly or shows obvious truncation (e.g., line items cut off, missing totals, text continues without conclusion)
    - Document is INCOMPLETE if critical signatures or authorization marks are missing for Faktur Pajak
    - Document is INCOMPLETE if the final total/closing section is missing or partial
    - Document is COMPLETE if all major sections and signature areas are present (even if some optional fields are missing)
    - Look for visual/textual indicators of signature areas: "Signature:", "Authorized by:", "Signed", "TTD" (Tanda Tangan), signature lines, or actual signature marks

    Provide the classification result in the following JSON format:
    {{
        "classification": "<Invoice | Tax Invoice (Faktur Pajak) | General Ledger | Unknown>",
        "is_document_complete": <true | false>,
        "confidence_score": <float between 0 and 1>,
        "completeness_reason": "<brief explanation of why document is complete or incomplete>"
    }}

    Here is the document content to classify:
    \"\"\"{document_content}\"\"\"

    Please analyze the document and provide the classification result as specified. Also, indicate whether the document appears to be complete and provide a confidence score for your classification. Include a brief reason explaining the completeness assessment.

    # Remember:
    - Focus on key indicators within the document content to determine its category.
    - If the document does not clearly fit into any of the categories, classify it as "Unknown".
    - **DEFINITIVE FAKTUR PAJAK INDICATOR**: Presence of "PPnBM" AND "Potongan Harga" columns = Tax Invoice (100% certain)
    - **CRITICAL FOR CONTINUATION PAGES**: Look for tax-specific column headers ("Harga Jual/Penggantian", "Nama Barang Kena Pajak", "PPnBM", "Potongan Harga") as PRIMARY indicators
    - Column headers are MORE RELIABLE than NPWP for middle pages (NPWP only appears on first page)
    - Presence of NPWP for BOTH seller and buyer indicates first page of Tax Invoice
    - Sequential item numbering + tax-specific columns = Tax Invoice continuation page
    - Look for signature indicators: "TTD", "Signature", "Authorized", signature lines (------), or actual signature marks.
    - For Faktur Pajak, presence of signature/authorization area is CRITICAL for determining completeness.

    """

def get_invoice_extraction_prompt(document_content: str) -> str:
    return f"""
    You are an expert AI specialized in extracting structured data from invoices. Your task is to analyze the provided invoice content and extract key information into a structured JSON format matching the Invoice domain model.

    Provide the extraction result in the following JSON format:

    {{
        "invoiceId": "<string: unique identifier for the invoice>",
        "invoiceNumber": "<string: invoice number from the document>",
        "urn": "<string: Unique Reference Number>",
        "projectNumber": "<string: project number reference>",
        "invoiceDetail": [
            {{
                "invoiceDetailId": "<string: unique identifier for line item>",
                "itemName": "<string: name of the item/service>",
                "quantity": <number: quantity of items>,
                "unitPrice": <number: unit price per item>,
                "taxPercentage": <number: tax percentage (0-100)>,
                "discountPercentage": <number: discount percentage (0-100)>,
                "extendedPrice": <number: calculated amount after tax and discount>
            }}
        ],
        "subTotalAmount": <number: subtotal amount before tax>,
        "vatPercentage": <number or null: VAT percentage (0-100)>,
        "vatAmount": <number: VAT amount>,
        "discountAmount": <number: total discount amount (default 0.0)>,
        "whtPercentage": <number or null: Withholding tax percentage (0-100)>,
        "whtAmount": <number or null: Withholding tax amount>,
        "totalAmount": <number: final total invoice amount>,
        "currency": "<string: ISO 4217 currency code (e.g., USD, IDR, SGD)>",
        "createdAt": "<string: ISO timestamp when invoice was created>",
        "updatedAt": "<string: ISO timestamp when invoice was last updated>"
    }}

    Guidelines for extraction:
    - Extract all visible line items with their quantities, unit prices, and amounts
    - Calculate extended prices based on quantity × unit price with tax and discount adjustments
    - Identify VAT/tax percentages and amounts from the invoice
    - Capture withholding tax information if present
    - Use ISO 8601 format for timestamps (e.g., 2025-12-29T11:30:00Z)
    - If a field is not present in the document, use null for optional fields or 0 for numeric defaults
    - Ensure all amounts are accurate and consistent with the document

    Here is the invoice content to extract data from:
    \"\"\"{document_content}\"\"\"

    """

def get_tax_invoice_extraction_prompt(document_content: str) -> str:
    return f"""
    You are an expert AI specialized in extracting structured data from tax invoices (Faktur Pajak). Your task is to analyze the provided invoice content and extract key information into a structured JSON format matching the TaxInvoice domain model.

    Provide the extraction result in the following JSON format:

    {{
        "taxInvoiceId": "<string: unique identifier for the tax invoice>",
        "urn": "<string: Unique Reference Number>",
        "taxInvoiceNumber": "<string: tax invoice number or code from the document>",
        "invoiceNumber": "<string: invoice number or code>",
        "taxInvoiceDate": "<string: date of tax invoice in ISO format (YYYY-MM-DD)>",
        "namaPengusahaKenaPajak": "<string: Nama Pengusaha Kena Pajak (Seller/Vendor name)>",
        "alamatPengusahaKenaPajak": "<string: Alamat Pengusaha Kena Pajak (Seller address)>",
        "npwpPengusahaKenaPajak": "<string: NPWP Pengusaha Kena Pajak (Seller tax ID)>",
        "namaPembeliKenaPajak": "<string: Nama Pembeli Kena Pajak (Buyer name)>",
        "alamatPembeliKenaPajak": "<string: Alamat Pembeli Kena Pajak (Buyer address)>",
        "npwpPembeliKenaPajak": "<string or null: NPWP Pembeli Kena Pajak (Buyer tax ID, optional)>",
        "nikPembeliKenaPajak": "<string or null: NIK Pembeli Kena Pajak (Buyer national ID, optional)>",
        "nomorPasporPembeliKenaPajak": "<string or null: Nomor Paspor Pembeli Kena Pajak (Buyer passport number, optional)>",
        "emailPembeliKenaPajak": "<string: Email Pembeli Kena Pajak (Buyer email)>",
        "taxInvoiceDetail": [
            {{
                "taxInvoiceDetailId": "<string: unique identifier for line item>",
                "itemCode": "<string: item/product code>",
                "itemName": "<string: item/product name>",
                "price": <number: unit price>,
                "quantity": <number: quantity of items>,
                "taxBaseWht": <number: tax base for withholding tax>
            }}
        ],
        "totalTaxBaseWht": <number: Total Harga Jual / Penggantian / Uang Muka / Termin (Total tax base)>,
        "dikurangiPotonganHarga": <number: Dikurangi potongan harga (Less: price discount, default 0.0)>,
        "dikurangiUangMukaYangTelahDiterima": <number: Dikurangi uang muka yang telah diterima (Less: advance payment received, default 0.0)>,
        "dasarPengenaanPajak": <number: Dasar Pengenaan Pajak (Tax base)>,
        "jumlahPpn": <number: Jumlah PPN (Total PPN/VAT, default 0.0)>,
        "jumlahPpnbm": <number: Jumlah PPnBM (Total PPNBM/Luxury Tax, default 0.0)>,
        "createdAt": "<string: ISO timestamp when tax invoice was created (YYYY-MM-DDTHH:MM:SSZ)>",
        "updatedAt": "<string: ISO timestamp when tax invoice was last updated (YYYY-MM-DDTHH:MM:SSZ)>"
    }}

    Guidelines for extraction:
    - Extract all visible line items with item codes, names, quantities, and prices
    - Calculate tax base for each line item (quantity × price)
    - Identify seller (Pengusaha Kena Pajak) and buyer (Pembeli Kena Pajak) information
    - Extract NPWP (tax ID) for both seller and buyer (buyer NPWP may be optional, use NIK or passport if available)
    - Extract tax information including PPN (VAT) and PPnBM (Luxury Tax)
    - Calculate totals: total tax base, price discounts, advance payments received, final tax base
    - Use ISO 8601 format for dates (YYYY-MM-DD) and timestamps (YYYY-MM-DDTHH:MM:SSZ)
    - If a field is not present in the document, use null for optional fields or 0 for numeric defaults
    - Ensure all amounts are accurate and consistent with the document
    - The URN should already be extracted separately using regex from the beginning of the document

    Here is the tax invoice content to extract data from:
    \"\"\"{document_content}\"\"\"

    """
