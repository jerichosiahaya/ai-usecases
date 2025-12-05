from loguru import logger
from typing import Optional, List
from src.repository.database import CosmosDB, CosmosDBRepository
from src.domain.candidate import Candidate, CandidateResponse, LegalDocument
from src.llm.llm_sk import LLMService

class CandidateService:
    def __init__(self, cosmosdb: CosmosDB, llm_service: LLMService):
        self.cosmosdb = cosmosdb
        self.llm_service = llm_service
        # Use 'candidates' container, or create with default if not specified
        self.candidate_repo = CosmosDBRepository(cosmosdb, Candidate, container_name="candidates")

    async def get_candidate(self, candidate_id: str) -> Optional[CandidateResponse]:
        """
        Use case: Retrieve a single candidate by ID.
        
        Args:
            candidate_id: The candidate ID to retrieve
            
        Returns:
            CandidateResponse object if found, None otherwise
        """
        try:
            candidate = self.candidate_repo.get_by_id(candidate_id, id_field="candidateId")
            if candidate:
                return CandidateResponse(**candidate.model_dump())
            return None
        except Exception as e:
            logger.error(f"Error in get_candidate use case: {e}")
            raise

    async def list_candidates(self, limit: int = 100) -> List[CandidateResponse]:
        """
        Use case: Retrieve all candidates.
        
        Args:
            limit: Maximum number of candidates to retrieve
            
        Returns:
            List of CandidateResponse objects
        """
        try:
            candidates = self.candidate_repo.get_all(limit)
            return [CandidateResponse(**c.model_dump()) for c in candidates]
        except Exception as e:
            logger.error(f"Error in list_candidates use case: {e}")
            raise

    async def get_candidates_by_status(self, status: str, limit: int = 100) -> List[CandidateResponse]:
        """
        Use case: Retrieve candidates filtered by status.
        
        Args:
            status: The status to filter by
            limit: Maximum number of candidates to retrieve
            
        Returns:
            List of CandidateResponse objects
        """
        try:
            candidates = self.candidate_repo.get_by_field("status", status, limit)
            return [CandidateResponse(**c.model_dump()) for c in candidates]
        except Exception as e:
            logger.error(f"Error in get_candidates_by_status use case: {e}")
            raise

    async def get_candidates_by_position(self, position: str, limit: int = 100) -> List[CandidateResponse]:
        """
        Use case: Retrieve candidates filtered by position.
        
        Args:
            position: The position to filter by
            limit: Maximum number of candidates to retrieve
            
        Returns:
            List of CandidateResponse objects
        """
        try:
            candidates = self.candidate_repo.get_by_field("position", position, limit)
            return [CandidateResponse(**c.model_dump()) for c in candidates]
        except Exception as e:
            logger.error(f"Error in get_candidates_by_position use case: {e}")
            raise

    async def update_candidate(self, candidate_id: str, candidate_data: dict) -> Optional[CandidateResponse]:
        try:
            # Get existing candidate (Model)
            existing_candidate = self.candidate_repo.get_by_id(candidate_id, id_field="candidateId")
            if not existing_candidate:
                return None
            
            discrepancy_results = await self.llm_service.discrepancy_analysis(existing_candidate.model_copy(update=candidate_data))
            
            # Get existing raw candidate (Dict) to preserve extra fields and casing
            existing_candidate_raw = self.candidate_repo.get_raw_by_id(candidate_id, id_field="candidateId")

            # Merge existing data with new data
            # We use model_dump() to get the current state as a dict (snake_case keys)
            current_data = existing_candidate.model_dump()
            
            # Handle legal_documents specially: replace by type instead of appending
            if "legal_documents" in candidate_data and candidate_data["legal_documents"]:
                new_legal_docs = candidate_data["legal_documents"]
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
                
                # Remove legal_documents from candidate_data
                candidate_data.pop("legal_documents")
                
                # Update with new data (excluding legal_documents)
                current_data.update(candidate_data)
                
                # Now set the merged legal_documents
                current_data["legal_documents"] = merged_legal_docs
            else:
                # Update with new data if legal_documents not provided
                current_data.update(candidate_data)
            
            # Create new Candidate object to validate
            updated_candidate = Candidate(**current_data)
            
            # Prepare data for saving
            # Use by_alias=True to get camelCase keys (matching DB schema)
            updated_data_camel = updated_candidate.model_dump(by_alias=True)
            
            # Merge into raw data to preserve extra fields
            if existing_candidate_raw:
                existing_candidate_raw.update(updated_data_camel)
                item_to_save = existing_candidate_raw
            else:
                item_to_save = updated_data_camel
            
            # Insert discrepancy results into discrepancies field
            if discrepancy_results and "discrepancies" in discrepancy_results:
                item_to_save["discrepancies"] = discrepancy_results["discrepancies"]
            
            # Save to DB using raw update to preserve structure
            self.candidate_repo.update_item(item=item_to_save)
            
            return CandidateResponse(**updated_candidate.model_dump())
        except Exception as e:
            logger.error(f"Error in update_candidate use case: {e}")
            raise
