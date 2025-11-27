from loguru import logger
from typing import Optional, List
from src.repository.database import CosmosDB, CosmosDBRepository
from src.domain.candidate import Candidate, CandidateResponse

class CandidateService:
    def __init__(self, cosmosdb: CosmosDB):
        self.cosmosdb = cosmosdb
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
        """
        Use case: Update a candidate.
        
        Args:
            candidate_id: The candidate ID to update
            candidate_data: The new candidate data (partial or full)
            
        Returns:
            CandidateResponse object if updated, None otherwise
        """
        try:
            # Get existing candidate (Model)
            existing_candidate = self.candidate_repo.get_by_id(candidate_id, id_field="candidateId")
            if not existing_candidate:
                return None
            
            # Get existing raw candidate (Dict) to preserve extra fields and casing
            existing_candidate_raw = self.candidate_repo.get_raw_by_id(candidate_id, id_field="candidateId")

            # Merge existing data with new data
            # We use model_dump() to get the current state as a dict (snake_case keys)
            current_data = existing_candidate.model_dump()
            
            # Update with new data
            # We assume candidate_data keys match the model fields (snake_case)
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
            
            # Save to DB using raw update to preserve structure
            self.candidate_repo.update_item(item=item_to_save)
            
            return CandidateResponse(**updated_candidate.model_dump())
        except Exception as e:
            logger.error(f"Error in update_candidate use case: {e}")
            raise
