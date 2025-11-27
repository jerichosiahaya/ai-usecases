from src.config.env import AppConfig
from azure.cosmos import CosmosClient
import uuid
from datetime import datetime
from loguru import logger
from typing import Optional, List, Type, TypeVar, Dict, Any

T = TypeVar('T')

def convert_camel_to_snake(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert camelCase keys in a dictionary to snake_case recursively.
    This helps with Pydantic model instantiation when data comes from CosmosDB.
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        # Convert camelCase to snake_case
        snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
        
        # Recursively convert nested dictionaries
        if isinstance(value, dict):
            result[snake_key] = convert_camel_to_snake(value)
        # Recursively convert items in lists (for nested objects in arrays)
        elif isinstance(value, list):
            result[snake_key] = [
                convert_camel_to_snake(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[snake_key] = value
    
    return result

class CosmosDB:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = CosmosClient.from_connection_string(self.config.COSMOSDB_CONNECTION_STRING)
        self.database = self.client.get_database_client(self.config.COSMOSDB_DATABASE)
        self.containers = {}  # Dictionary to hold multiple containers
        self._load_container(self.config.COSMOSDB_CONTAINER, "default")

    def _load_container(self, container_name: str, alias: str = None):
        """
        Load a container by name and optionally assign an alias.
        
        Args:
            container_name: The name of the container in CosmosDB
            alias: Optional alias for easy reference (default: use container_name)
        """
        key = alias or container_name
        self.containers[key] = self.database.get_container_client(container_name)
        if key == "default":
            self.container = self.containers[key]  # Keep default for backward compatibility

    def get_container(self, container_name: str):
        """
        Get a specific container by name or alias.
        
        Args:
            container_name: The container name or alias
            
        Returns:
            The container client
        """
        if container_name not in self.containers:
            self._load_container(container_name, container_name)
        return self.containers[container_name]

    def insert_items(self, vector, candidate_id, name, skills, work_history, education_history):
        chat_item = {
            'id': str(uuid.uuid4()),
            'candidateId': candidate_id,
            'name': name,
            'embeddings': vector,
            'skills': skills,
            'workHistory': work_history,
            'educationHistory': education_history,
            'timestamp': datetime.utcnow().isoformat(),
        }
        response = self.container.create_item(body=chat_item)
        return response

    def query_items(self, query_vector, num_results: int = 5):
        try:
            query = f"""
            SELECT TOP @num_results c.id, c.candidateId, c.name,
            VectorDistance(c.embeddings, @embedding) AS SimilarityScore 
            FROM c 
            ORDER BY VectorDistance(c.embeddings, @embedding)
            """
            items = self.container.query_items(
                query=query,
                parameters=[
                    {"name": "@num_results", "value": num_results},
                    {"name": "@embedding", "value": query_vector}
                ],
                enable_cross_partition_query=True
            )

            recommendations = []
            for item in items:
                recommendations.append({
                    "id": item.get("id"),
                    "candidate_id": item.get("candidateId"),
                    "name": item.get("name"),
                    "similarity_score": item.get("SimilarityScore")
                })

            return recommendations
        except Exception as e:
            logger.error(f"Error querying items: {e}")
            raise ValueError(f"Error querying items: {e}")


class CosmosDBRepository:
    """
    Generic CosmosDB repository for handling CRUD operations.
    Supports multiple containers through the CosmosDB client.
    """
    
    def __init__(self, cosmosdb: CosmosDB, model_class: Type[T], container_name: str = "default"):
        """
        Initialize the repository with a CosmosDB client, model class, and container name.
        
        Args:
            cosmosdb: CosmosDB client instance
            model_class: Pydantic model class for data mapping
            container_name: The name or alias of the container to use (default: "default")
        """
        self.cosmosdb = cosmosdb
        self.model_class = model_class
        self.container = cosmosdb.get_container(container_name)

    def get_by_id(self, item_id: str, id_field: str = "id") -> Optional[T]:
        """
        Retrieve an item from CosmosDB by ID.
        
        Args:
            item_id: The item ID to search for
            id_field: The field name to search in (default: "id")
            
        Returns:
            Model instance if found, None otherwise
        """
        try:
            query = f"SELECT * FROM c WHERE c.{id_field} = @item_id"
            items = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@item_id", "value": item_id}],
                enable_cross_partition_query=True
            ))
            
            if items and len(items) > 0:
                # Convert camelCase to snake_case for Pydantic model
                converted_item = convert_camel_to_snake(items[0])
                return self.model_class(**converted_item)
            return None
        except Exception as e:
            logger.error(f"Error retrieving item by ID: {e}")
            raise

    def get_all(self, limit: int = 100) -> List[T]:
        """
        Retrieve all items from CosmosDB.
        
        Args:
            limit: Maximum number of items to retrieve
            
        Returns:
            List of model instances
        """
        try:
            query = f"SELECT * FROM c OFFSET 0 LIMIT {limit}"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            # Convert camelCase to snake_case for Pydantic model
            return [self.model_class(**convert_camel_to_snake(item)) for item in items]
        except Exception as e:
            logger.error(f"Error retrieving all items: {e}")
            raise

    def get_by_field(self, field_name: str, field_value: Any, limit: int = 100) -> List[T]:
        """
        Retrieve items filtered by a specific field.
        
        Args:
            field_name: The field name to filter by
            field_value: The value to filter for
            limit: Maximum number of items to retrieve
            
        Returns:
            List of model instances matching the filter
        """
        try:
            query = f"SELECT * FROM c WHERE c.{field_name} = @field_value OFFSET 0 LIMIT {limit}"
            items = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@field_value", "value": field_value}],
                enable_cross_partition_query=True
            ))
            
            # Convert camelCase to snake_case for Pydantic model
            return [self.model_class(**convert_camel_to_snake(item)) for item in items]
        except Exception as e:
            logger.error(f"Error retrieving items by field {field_name}: {e}")
            raise

    def get_by_multiple_fields(self, filters: Dict[str, Any], limit: int = 100) -> List[T]:
        """
        Retrieve items filtered by multiple fields.
        
        Args:
            filters: Dictionary of field names and values to filter by
            limit: Maximum number of items to retrieve
            
        Returns:
            List of model instances matching all filters
        """
        try:
            # Build WHERE clause
            where_clauses = [f"c.{field} = @{field}" for field in filters.keys()]
            where_clause = " AND ".join(where_clauses)
            
            query = f"SELECT * FROM c WHERE {where_clause} OFFSET 0 LIMIT {limit}"
            
            # Build parameters
            parameters = [{"name": f"@{field}", "value": value} for field, value in filters.items()]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            # Convert camelCase to snake_case for Pydantic model
            return [self.model_class(**convert_camel_to_snake(item)) for item in items]
        except Exception as e:
            logger.error(f"Error retrieving items by multiple fields: {e}")
            raise

    def insert(self, item: T) -> Dict[str, Any]:
        """
        Insert an item into CosmosDB.
        
        Args:
            item: The model instance to insert
            
        Returns:
            The response from CosmosDB
        """
        try:
            item_dict = item.model_dump() if hasattr(item, 'model_dump') else item.__dict__
            response = self.container.create_item(body=item_dict)
            return response
        except Exception as e:
            logger.error(f"Error inserting item: {e}")
            raise

    def update(self, item_id: str, item: T, id_field: str = "id") -> Dict[str, Any]:
        """
        Update an item in CosmosDB.
        
        Args:
            item_id: The ID of the item to update
            item: The updated model instance
            id_field: The field name that contains the ID
            
        Returns:
            The response from CosmosDB
        """
        try:
            item_dict = item.model_dump() if hasattr(item, 'model_dump') else item.__dict__
            response = self.container.replace_item(item=item_dict)
            return response
        except Exception as e:
            logger.error(f"Error updating item: {e}")
            raise

    def delete(self, item_id: str, id_field: str = "id") -> None:
        """
        Delete an item from CosmosDB.
        
        Args:
            item_id: The ID of the item to delete
            id_field: The field name that contains the ID
        """
        try:
            # First, get the item to find its document ID
            item = self.get_by_id(item_id, id_field)
            if item:
                item_dict = item.model_dump() if hasattr(item, 'model_dump') else item.__dict__
                self.container.delete_item(item=item_dict)
            else:
                logger.warning(f"Item with {id_field}={item_id} not found for deletion")
        except Exception as e:
            logger.error(f"Error deleting item: {e}")
            raise

    def query(self, query_string: str, parameters: List[Dict[str, Any]] = None) -> List[T]:
        """
        Execute a custom query against CosmosDB.
        
        Args:
            query_string: The SQL query string
            parameters: List of query parameters
            
        Returns:
            List of model instances matching the query
        """
        try:
            items = list(self.container.query_items(
                query=query_string,
                parameters=parameters or [],
                enable_cross_partition_query=True
            ))
            
            # Convert camelCase to snake_case for Pydantic model
            return [self.model_class(**convert_camel_to_snake(item)) for item in items]
        except Exception as e:
            logger.error(f"Error executing custom query: {e}")
            raise

    def get_raw_by_id(self, item_id: str, id_field: str = "id") -> Optional[Dict[str, Any]]:
        """
        Retrieve a raw item (dict) from CosmosDB by ID.
        
        Args:
            item_id: The item ID to search for
            id_field: The field name to search in (default: "id")
            
        Returns:
            Dictionary representing the item if found, None otherwise
        """
        try:
            query = f"SELECT * FROM c WHERE c.{id_field} = @item_id"
            items = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@item_id", "value": item_id}],
                enable_cross_partition_query=True
            ))
            
            if items and len(items) > 0:
                return items[0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving raw item by ID: {e}")
            raise

    def update_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a raw item in CosmosDB.
        
        Args:
            item: The dictionary containing the item data
            
        Returns:
            The response from CosmosDB
        """
        try:
            response = self.container.replace_item(item=item, body=item)
            return response
        except Exception as e:
            logger.error(f"Error updating raw item: {e}")
            raise