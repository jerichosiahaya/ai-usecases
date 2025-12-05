from typing import List
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatPromptExecutionSettings
from loguru import logger
from src.llm.prompt import _get_cv_extractor_system_prompt, _get_predefined_score_system_prompt, _get_kartu_keluarga_document_analysis, _get_legal_documents_classification_prompt, _get_discrepancy_analysis_prompt, _get_buku_tabungan_document_analysis, _get_ktp_document_analysis, _get_offering_letter_content_analysis_prompt
from src.domain.cv_extractor import CVAttributeExtractionResponse
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
import json
from src.domain.cv_scoring import CVScoringResponse, CVScoringAttribute
from src.domain.document_classification import ClassificationResult
from src.domain.candidate import Candidate, ListDiscrepancyResponse
from src.domain.document_analyzer import KartuKeluarga, BukuTabungan, KTP, OfferingLetterContent

class LLMService:
    def __init__(self, service_id: str = "default_service", azure_openai_key=None, azure_openai_endpoint=None, azure_openai_deployment=None, azure_openai_version=None):

        self.azure_chat_completion = AzureChatCompletion(
            service_id=service_id,
            deployment_name=azure_openai_deployment,
            api_version=azure_openai_version,
            api_key=azure_openai_key,
            endpoint=azure_openai_endpoint
        )

    async def extract_cv_attributes(self, cv_text: str) -> dict:
        try:
            instructions = _get_cv_extractor_system_prompt()
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = CVAttributeExtractionResponse

            prompt = f"""
            Here is the CV text:
            {cv_text}
            """

            chat_content = ChatMessageContent(
                role=AuthorRole.USER,
                items=[
                    TextContent(text=prompt)
                ]
            )

            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="CVExtractorAgent",
                instructions=instructions,
                arguments=KernelArguments(settings=settings)
            ) 

            response = await agent.get_response(chat_content)

            return json.loads(str(response.content))
        
        except Exception as e:
            raise Exception(f"Error extracting CV attributes: {str(e)}")
        
    async def score_cv(self, predefined_score: str, candidate_data: str) -> str:
        try:
            instructions = _get_predefined_score_system_prompt(predefined_score)
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = CVScoringResponse

            prompt = f"""
            Candidate:
            {candidate_data}
            """

            chat_content = ChatMessageContent(
                role=AuthorRole.USER,
                items=[
                    TextContent(text=prompt)
                ]
            )

            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="CVScoringAgent",
                instructions=instructions,
                arguments=KernelArguments(settings=settings)
            )

            response = await agent.get_response(chat_content)

            return json.loads(str(response.content))

        except Exception as e:
            raise Exception(f"Error scoring CV: {str(e)}")
    
    async def kartu_keluarga_extractor(self, kk_text: str) -> str:
        try:
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = KartuKeluarga

            prompt = f"""
            Here is the Kartu Keluarga text:
            {kk_text}
            """

            chat_content = ChatMessageContent(
                role=AuthorRole.USER,
                items=[
                    TextContent(text=prompt)
                ]
            )

            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="KartuKeluargaExtractorAgent",
                instructions=_get_kartu_keluarga_document_analysis(),
                arguments=KernelArguments(settings=settings)
            )

            response = await agent.get_response(chat_content)

            return json.loads(str(response.content))
        
        except Exception as e:
            raise Exception(f"Error extracting Kartu Keluarga information: {str(e)}")
        
    async def buku_tabungan_extractor(self, buku_tabungan_text: str) -> str:
        try:
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = BukuTabungan

            prompt = f"""
            Here is the Buku Tabungan text:
            {buku_tabungan_text}
            """

            chat_content = ChatMessageContent(
                role=AuthorRole.USER,
                items=[
                    TextContent(text=prompt)
                ]
            )

            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="BukuTabunganExtractorAgent",
                instructions=_get_buku_tabungan_document_analysis(),
                arguments=KernelArguments(settings=settings)
            )

            response = await agent.get_response(chat_content)

            return json.loads(str(response.content))
        
        except Exception as e:
            raise Exception(f"Error extracting Buku Tabungan information: {str(e)}")
        
    async def ktp_extractor(self, ktp_text: str) -> str:
        try:
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = KTP

            prompt = f"""
            Here is the KTP text:
            {ktp_text}
            """

            chat_content = ChatMessageContent(
                role=AuthorRole.USER,
                items=[
                    TextContent(text=prompt)
                ]
            )

            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="KTPExtractorAgent",
                instructions=_get_ktp_document_analysis(),
                arguments=KernelArguments(settings=settings)
            )

            response = await agent.get_response(chat_content)

            return json.loads(str(response.content))
        
        except Exception as e:
            raise Exception(f"Error extracting Buku Tabungan information: {str(e)}")
        
    async def legal_document_classification(self, document_text: str) -> str:
        try:
            settings = OpenAIChatPromptExecutionSettings()

            prompt = f"""
            Here is the legal document text:
            {document_text}
            """

            chat_content = ChatMessageContent(
                role=AuthorRole.USER,
                items=[
                    TextContent(text=prompt)
                ]
            )

            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="LegalDocumentClassificationAgent",
                instructions=_get_legal_documents_classification_prompt(),
                arguments=KernelArguments(settings=settings)
            )

            response = await agent.get_response(chat_content)

            return json.loads(str(response.content))
        
        except Exception as e:
            raise Exception(f"Error classifying legal document: {str(e)}")
        
    async def discrepancy_analysis(self, candidate_data: Candidate) -> str:
        try:

            # pop discrepancies field from candidate_data if exists
            if hasattr(candidate_data, 'discrepancies'):
                del candidate_data.discrepancies

            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = ListDiscrepancyResponse

            prompt = f"""
            Analyze the following candidate data for discrepancies:
            {candidate_data}
            """

            chat_content = ChatMessageContent(
                role=AuthorRole.USER,
                items=[
                    TextContent(text=prompt)
                ]
            )

            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="DiscrepancyAnalysisAgent",
                instructions=_get_discrepancy_analysis_prompt(),
                arguments=KernelArguments(settings=settings)
            )

            response = await agent.get_response(chat_content)

            return json.loads(str(response.content))
        
        except Exception as e:
            raise Exception(f"Error analyzing discrepancies: {str(e)}")
        
    async def offering_letter_content_analysis(self, offering_letter_content: str) -> str:
        try:

            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = OfferingLetterContent

            prompt = f"""
            Analyze the following offering letter content:
            {offering_letter_content}
            """

            chat_content = ChatMessageContent(
                role=AuthorRole.USER,
                items=[
                    TextContent(text=prompt)
                ]
            )

            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="OfferingLetterContentAnalysisAgent",
                instructions=_get_offering_letter_content_analysis_prompt(),
                arguments=KernelArguments(settings=settings)
            )

            response = await agent.get_response(chat_content)

            return json.loads(str(response.content))
        
        except Exception as e:
            raise Exception(f"Error analyzing offering letter content: {str(e)}")

