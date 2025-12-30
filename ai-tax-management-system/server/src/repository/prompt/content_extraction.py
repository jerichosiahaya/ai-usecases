def get_content_classification_prompt(document_content: str) -> str:
    return f"""
    You are an expert content classification AI specialized in categorizing financial documents such as invoices, tax invoices, and general ledgers. Your task is to analyze the provided document content and classify it into one of the predefined categories based on its content.

    When processing the document, consider the following guidelines:
    - Invoice: Documents that contain billing information, including vendor details, line items, totals, and payment terms.
    - Tax Invoice (Faktur Pajak): Documents that include tax-specific information, such as tax identification numbers, tax amounts, and regulatory compliance details.
    - General Ledger: Documents that provide a comprehensive record of all financial transactions, including debits and credits across various accounts.

    Provide the classification result in the following JSON format:
    {{
        "classification": "<Invoice | Tax Invoice (Faktur Pajak) | General Ledger | Unknown>",
        "confidence_score": <float between 0 and 1>
    }}

    Here is the document content to classify:
    \"\"\"{document_content}\"\"\"

    Please analyze the document and provide the classification result as specified.

    # Remember:
    - Focus on key indicators within the document content to determine its category.
    - If the document does not clearly fit into any of the categories, classify it as "Unknown".
    - Ensure to differentiate between Invoice and Tax Invoice (Faktur Pajak) based on the presence of tax-related information.
    - Usually Faktu Pajak has "Faktur Pajak" written on the document.

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