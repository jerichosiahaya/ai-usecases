from src.domain.gl_transaction import GLTransaction, GLReconItem
from src.domain.tax_invoice import TaxInvoice
from src.domain.invoice import Invoice
from typing import List
from loguru import logger
from src.repository.database import AzureCosmosDBRepository

class TaxManagementUseCase:
    def __init__(self, azure_cosmos_repo: AzureCosmosDBRepository):
        self.azure_cosmos_repo = azure_cosmos_repo

    def get_gl_transactions(self, urn: str = None) -> List[GLTransaction]:
        try:
            if urn:
                result = self.azure_cosmos_repo.query_documents(
                    container_id="gl-transactions",
                    query_filter=f"c.urn = '{urn}'"
                )
            else:
                result = self.azure_cosmos_repo.query_documents(container_id="gl-transactions")
            return [GLTransaction(**item) for item in result]
        except Exception as e:
            logger.error(f"Error retrieving G/L transactions: {e}")
            raise e

    def get_tax_invoices(self, urn: str = None) -> List[TaxInvoice]:
        try:
            if urn:
                result = self.azure_cosmos_repo.query_documents(
                    container_id="tax-invoices",
                    query_filter=f"c.urn = '{urn}'"
                )
            else:
                result = self.azure_cosmos_repo.query_documents(container_id="tax-invoices")
            return [TaxInvoice(**item) for item in result]
        except Exception as e:
            logger.error(f"Error retrieving tax invoices: {e}")
            raise e

    def get_invoices(self, urn: str = None) -> List[Invoice]:
        try:
            if urn:
                result = self.azure_cosmos_repo.query_documents(
                    container_id="invoices",
                    query_filter=f"c.urn = '{urn}'"
                )
            else:
                result = self.azure_cosmos_repo.query_documents(container_id="invoices")
            return [Invoice(**item) for item in result]
        except Exception as e:
            logger.error(f"Error retrieving invoices: {e}")
            raise e