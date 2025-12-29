from enum import Enum

class ResponseStatus(str, Enum):
    Success = "Success"
    Failed = "Failed"
    Error = "Error"

class Environment(str, Enum):
    Development = "development"
    Production = "production"

class ContentType(str, Enum):
    Invoice = "Invoice"
    TaxInvoice = "Tax Invoice (Faktur Pajak)"
    GeneralLedger = "General Ledger"
    Unknown = "Unknown"