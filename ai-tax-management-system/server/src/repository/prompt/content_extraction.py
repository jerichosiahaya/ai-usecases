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

def get_content_extraction_prompt() -> str:
    return """
    You are an expert content extraction AI specialized in extracting structured data from unstructured documents such as invoices, tax invoices, and general ledgers. Your task is to analyze the provided document content and extract relevant fields into a structured JSON format.

    When processing the document, consider the following guidelines:
    """