from loguru import logger
from typing import Optional, List
from src.repository.database import CosmosDB, CosmosDBRepository
from src.domain.employee import Employee, LegalDocument
from src.llm.llm_sk import LLMService

class EmployeeService:
    def __init__(self, cosmosdb: CosmosDB, llm_service: LLMService):
        self.cosmosdb = cosmosdb
        self.llm_service = llm_service
        # Use 'employees' container, or create with default if not specified
        self.employee_repo = CosmosDBRepository(cosmosdb, Employee, container_name="employees")

    async def get_employee(self, employee_id: str) -> Optional[Employee]:
        """
        Use case: Retrieve a single employee by ID.
        
        Args:
            employee_id: The employee ID to retrieve
            
        Returns:
            CandidateResponse object if found, None otherwise
        """
        try:
            employee = self.employee_repo.get_by_id(employee_id, id_field="employeeId")
            if employee:
                return Employee(**employee.model_dump())
            return None
        except Exception as e:
            logger.error(f"Error in get_employee use case: {e}")
            raise

    async def list_employees(self, limit: int = 100) -> List[Employee]:
        """
        Use case: Retrieve all employees.
        
        Args:
            limit: Maximum number of employees to retrieve
            
        Returns:
            List of Employee objects
        """
        try:
            employees = self.employee_repo.get_all(limit)
            return [Employee(**e.model_dump()) for e in employees]
        except Exception as e:
            logger.error(f"Error in list_employees use case: {e}")
            raise

    async def get_employees_by_status(self, status: str, limit: int = 100) -> List[Employee]:
        """
        Use case: Retrieve employees filtered by status.
        
        Args:
            status: The status to filter by
            limit: Maximum number of employees to retrieve
            
        Returns:
            List of Employee objects
        """
        try:
            employees = self.employee_repo.get_by_field("status", status, limit)
            return [Employee(**e.model_dump()) for e in employees]
        except Exception as e:
            logger.error(f"Error in get_employees_by_status use case: {e}")
            raise

    async def get_employees_by_position(self, position: str, limit: int = 100) -> List[Employee]:
        """
        Use case: Retrieve employees filtered by position.
        
        Args:
            position: The position to filter by
            limit: Maximum number of employees to retrieve
            
        Returns:
            List of Employee objects
        """
        try:
            employees = self.employee_repo.get_by_field("position", position, limit)
            return [Employee(**e.model_dump()) for e in employees]
        except Exception as e:
            logger.error(f"Error in get_employees_by_position use case: {e}")
            raise

    async def update_employee(self, employee_id: str, employee_data: dict) -> Optional[Employee]:
        try:
            # Get existing employee (Model)
            existing_employee = self.employee_repo.get_by_id(employee_id, id_field="employeeId")
            if not existing_employee:
                return None
            
            discrepancy_results = await self.llm_service.discrepancy_analysis(existing_employee.model_copy(update=employee_data))
            
            # Get existing raw employee (Dict) to preserve extra fields and casing
            existing_employee_raw = self.employee_repo.get_raw_by_id(employee_id, id_field="employeeId")

            # Merge existing data with new data
            # We use model_dump() to get the current state as a dict (snake_case keys)
            current_data = existing_employee.model_dump()
            
            # Handle legal_documents specially: replace by type instead of appending
            if "legal_documents" in employee_data and employee_data["legal_documents"]:
                new_legal_docs = employee_data["legal_documents"]
                existing_legal_docs = current_data.get("legal_documents", [])
                
                # Convert new docs to dicts for consistent handling
                new_legal_docs_dicts = [
                    doc.model_dump() if isinstance(doc, LegalDocument) else doc 
                    for doc in new_legal_docs
                ]
                
                # Convert existing docs to dicts
                existing_legal_docs_dicts = [
                    doc.model_dump() if isinstance(doc, LegalDocument) else doc 
                    for doc in existing_legal_docs
                ]
                
                # Get types of new documents
                new_types = {doc["type"] for doc in new_legal_docs_dicts}
                
                # Filter existing docs to exclude those with types being replaced
                filtered_existing = [
                    doc for doc in existing_legal_docs_dicts 
                    if doc.get("type") not in new_types
                ]
                
                # Combine: filtered existing + new documents
                merged_legal_docs = filtered_existing + new_legal_docs_dicts
                
                # Remove legal_documents from employee_data
                employee_data.pop("legal_documents")
                
                # Update with new data (excluding legal_documents)
                current_data.update(employee_data)
                
                # Now set the merged legal_documents
                current_data["legal_documents"] = merged_legal_docs
            else:
                # Update with new data if legal_documents not provided
                current_data.update(employee_data)
            
            # Create new Employee object to validate
            updated_employee = Employee(**current_data)
            
            # Prepare data for saving
            # Use by_alias=True to get camelCase keys (matching DB schema)
            updated_data_camel = updated_employee.model_dump(by_alias=True)
            
            # Merge into raw data to preserve extra fields
            if existing_employee:
                existing_employee_raw.update(updated_data_camel)
                item_to_save = existing_employee_raw
            else:
                item_to_save = updated_data_camel
            
            # Save to DB using raw update to preserve structure
            self.employee_repo.update_item(item=item_to_save)
            
            return Employee(**updated_employee.model_dump())
        except Exception as e:
            logger.error(f"Error in update_candidate use case: {e}")
            raise
