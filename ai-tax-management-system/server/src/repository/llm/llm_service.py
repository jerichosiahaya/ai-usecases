from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatPromptExecutionSettings
from loguru import logger
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents import ChatMessageContent, TextContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
import json
from typing import Optional, Any
from semantic_kernel.kernel_pydantic import KernelBaseModel

from src.config.env import AppConfig
from src.repository.prompt.content_extraction import get_content_classification_prompt, get_invoice_extraction_prompt, get_tax_invoice_extraction_prompt
from src.domain.invoice import Invoice
from src.domain.tax_invoice import TaxInvoice
from src.domain.gl_transaction import GLTransaction

class ClassificationResponse(KernelBaseModel):
    classification: str
    confidence_score: float
    is_document_complete: bool
    completeness_reason: Optional[str]

class LLMService:
    def __init__(self, service_id: str = "default_service", config: AppConfig = None):

        self.azure_chat_completion = AzureChatCompletion(
            service_id=service_id,
            deployment_name=config.AZURE_OPENAI_DEPLOYMENT_NAME,
            api_version=config.AZURE_OPENAI_API_VERSION,
            api_key=config.AZURE_OPENAI_API_KEY,
            endpoint=config.AZURE_OPENAI_API_BASE
        )

    async def get_content_classification(self, document_text: str) -> Optional[ClassificationResponse]:
        try:
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = ClassificationResponse
            instruction = get_content_classification_prompt(document_text)
            kernel = Kernel()
            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                kernel=kernel,
                name="ContentClassificationAgent",
                instructions=instruction,
                arguments=KernelArguments(settings=settings)
            )

            response = await agent.get_response()
            response_content = str(response.content)

            response_data = json.loads(response_content)

            return response_data

        except Exception as e:
            logger.error(f"Error getting content classification: {e}")
            return None
        
    async def get_invoice_extraction(self, document_text: str) -> Optional[Invoice]:
        try:
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = Invoice
            instruction = get_invoice_extraction_prompt(document_content=document_text)
            kernel = Kernel()
            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                kernel=kernel,
                name="InvoiceExtractionAgent",
                instructions=instruction,
                arguments=KernelArguments(settings=settings)
            )

            response = await agent.get_response()
            response_content = str(response.content)

            response_data = json.loads(response_content)

            return response_data

        except Exception as e:
            logger.error(f"Error getting content classification: {e}")
            return None
        
    async def get_tax_invoice_extraction(self, document_text: str) -> Optional[TaxInvoice]:

        try:
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = TaxInvoice
            instruction = get_tax_invoice_extraction_prompt(document_content=document_text)
            kernel = Kernel()
            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                kernel=kernel,
                name="TaxInvoiceExtractionAgent",
                instructions=instruction,
                arguments=KernelArguments(settings=settings)
            )

            response = await agent.get_response()
            response_content = str(response.content)

            response_data = json.loads(response_content)

            return response_data

        except Exception as e:
            logger.error(f"Error getting content classification: {e}")
            return None

    def get_gl_extraction(self):
        pass

        

    