from semantic_kernel.kernel_pydantic import KernelBaseModel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
import json
from prompt import _get_case_analysis_prompt, _get_file_description_prompt, _get_knowledge_graph_creation_prompt

class CaseFile(KernelBaseModel):
    filename: str
    content: str

class CaseDetails(KernelBaseModel):
    title: str
    description: str
    files: list[CaseFile]

class AnalysisData(KernelBaseModel):
    data_review: str
    root_cause_analysis: str
    hypothesis_testing: str

class ApplicableLaw(KernelBaseModel):
    law_name: str
    articles: list[str]
    violation_description: str
    penalty_level: str

class AnalysisResult(KernelBaseModel):
    case_main_category: str
    case_sub_category: str
    applicable_laws: list[ApplicableLaw]
    law_impact_analysis: str
    analysis: AnalysisData
    insights: list[str]
    recommendations: list[str]

class FileDescriptionResult(KernelBaseModel):
    description: str
    classification: str

class NodeInfo(KernelBaseModel):
    name: str

class EdgeInfo(KernelBaseModel):
    source: str
    target: str
    label: str

class KnowledgeGraphResult(KernelBaseModel):
    nodes: list[NodeInfo]
    edges: list[EdgeInfo]

class LLMService:
    def __init__(self, service_id: str = "default_service", azure_openai_key=None, azure_openai_endpoint=None, azure_openai_deployment=None, azure_openai_version=None):

        self.azure_chat_completion = AzureChatCompletion(
            service_id=service_id,
            deployment_name=azure_openai_deployment,
            api_version=azure_openai_version,
            api_key=azure_openai_key,
            endpoint=azure_openai_endpoint
        )

    async def analyze_case(self, case_details: CaseDetails) -> AnalysisResult:
        try:
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = AnalysisResult
            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="CaseAnalysisAgent",
                instructions=_get_case_analysis_prompt(case_details),
                arguments=KernelArguments(settings=settings)
            )
            response = await agent.get_response()
            if isinstance(str(response), str):
                try:
                    response_dict = json.loads(str(response))
                    return AnalysisResult(**response_dict)
                except json.JSONDecodeError:
                    return AnalysisResult(
                        insights=response_dict.get("insights", []),
                        recommendations=response_dict.get("recommendations", [])
                    )
            else:
                raise ValueError(f"Unexpected response type: {type(response)}")
        except Exception as e:
            print(f"Error during case analysis: {e}")
            raise

    async def analyze_file_description(self, file_name: str, file_content: str, case_details: CaseDetails) -> FileDescriptionResult:
        try:
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = FileDescriptionResult
            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="FileDescriptionAgent",
                instructions=_get_file_description_prompt(file_name, file_content, case_details),
                arguments=KernelArguments(settings=settings)
            )
            response = await agent.get_response()
            if isinstance(str(response), str):
                try:
                    response_dict = json.loads(str(response))
                    return FileDescriptionResult(**response_dict)
                except json.JSONDecodeError:
                    return FileDescriptionResult(description=str(response))
            else:
                raise ValueError(f"Unexpected response type: {type(response)}")
                
        except Exception as e:
            print(f"Error during file description analysis: {e}")
            raise 

    async def generate_knowledge_graph(self, case_details: CaseDetails) -> KnowledgeGraphResult:
        try:
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = KnowledgeGraphResult
            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="KnowledgeGraphAgent",
                instructions=_get_knowledge_graph_creation_prompt(case_details),
                arguments=KernelArguments(settings=settings)
            )
            response = await agent.get_response()
            if isinstance(str(response), str):
                try:
                    response_dict = json.loads(str(response))
                    return KnowledgeGraphResult(**response_dict)
                except json.JSONDecodeError:
                    return KnowledgeGraphResult(nodes={}, edges={})
            else:
                raise ValueError(f"Unexpected response type: {type(response)}")
                
        except Exception as e:
            print(f"Error during knowledge graph generation: {e}")
            raise