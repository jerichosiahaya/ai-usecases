from src.domain.gl_transaction import GLTransaction, GLReconItem
from src.domain.tax_invoice import TaxInvoice
from src.domain.invoice import Invoice
from typing import List, Tuple, Optional
from loguru import logger
from src.repository.database import AzureCosmosDBRepository

class TaxManagementUseCase:
    def __init__(self, azure_cosmos_repo: AzureCosmosDBRepository):
        self.azure_cosmos_repo = azure_cosmos_repo

    def get_gl_transactions(self, urn: str = None, page: int = 1, page_size: int = 10) -> Tuple[List[GLTransaction], int]:
        try:
            query_filter = f"c.urn = '{urn}'" if urn else None
            
            # Get total count
            total = self.azure_cosmos_repo.count_documents(
                container_id="gl-transactions",
                query_filter=query_filter
            )
            
            # Get paginated results
            offset = (page - 1) * page_size
            result = self.azure_cosmos_repo.query_documents(
                container_id="gl-transactions",
                query_filter=query_filter,
                offset=offset,
                limit=page_size
            )
            
            return [GLTransaction(**item) for item in result], total
        except Exception as e:
            logger.error(f"Error retrieving G/L transactions: {e}")
            raise e
    
    def get_gl_transaction_by_urn(self, urn: str) -> Optional[GLTransaction]:
        try:
            result = self.azure_cosmos_repo.query_documents(
                container_id="gl-transactions",
                query_filter=f"c.urn = '{urn}'",
                limit=1
            )
            if result:
                return GLTransaction(**result[0])
            return None
        except Exception as e:
            logger.error(f"Error retrieving G/L transaction by URN: {e}")
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

    def get_dashboard_stats(self) -> dict:
        try:
            gl_count = self.azure_cosmos_repo.count_documents(container_id="gl-transactions")
            tax_invoices_count = self.azure_cosmos_repo.count_documents(container_id="tax-invoices")
            invoices_count = self.azure_cosmos_repo.count_documents(container_id="invoices")
            
            return {
                "total_gl_transactions": gl_count,
                "total_tax_invoices": tax_invoices_count,
                "total_invoices": invoices_count
            }
        except Exception as e:
            logger.error(f"Error retrieving dashboard stats: {e}")
            raise e