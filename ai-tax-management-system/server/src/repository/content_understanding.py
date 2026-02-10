import requests
import json
from typing import Optional, Dict, Any
from src.config.env import AppConfig

class ContentUnderstandingRepository:
    """Repository for interacting with Azure AI Content Understanding API"""

    def __init__(self, config: AppConfig):
        """
        Initialize the repository with API configuration
        
        Args:
            config: ContentUnderstandingConfig with endpoint, api_key, and api_version
        """
        self.config = config
        self.base_url = config.CONTENT_UNDERSTANDING_ENDPOINT.rstrip("/")
        self.api_key = config.CONTENT_UNDERSTANDING_API_KEY
        self.api_version = config.CONTENT_UNDERSTANDING_API_VERSION

    def analyze_invoice(self, file_url: str) -> Dict[str, Any]:
        """
        Analyze an invoice document using the prebuilt-invoice analyzer
        
        Args:
            file_url: URL to the invoice document (PDF, image, etc.)
            
        Returns:
            Dictionary containing the analysis results
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response indicates an error
        """
        endpoint_url = (
            f"{self.base_url}/contentunderstanding/analyzers/prebuilt-invoice:analyze"
            f"?api-version={self.api_version}"
        )

        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "inputs": [
                {
                    "url": file_url
                }
            ]
        }

        response = requests.post(
            endpoint_url,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    def get_analyzer_results(self, request_id: str) -> Dict[str, Any]:
        """
        Retrieve analysis results using the request ID
        
        Args:
            request_id: The request ID returned from analyze_invoice
            
        Returns:
            Dictionary containing the analysis results
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response indicates an error
        """
        endpoint_url = (
            f"{self.base_url}/contentunderstanding/analyzerResults/{request_id}"
            f"?api-version={self.api_version}"
        )

        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
        }

        response = requests.get(
            endpoint_url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()
        return response.json()
    
