from enum import Enum

class ResponseStatus(str, Enum):
    Success = "Success"
    Failed = "Failed"
    Error = "Error"

class LLMVendor(str, Enum):
    OpenAI = "openai"
    VertexAI = "vertexai"

class LLMModel(str, Enum):
    GPT4_1_Mini = "gpt-4.1-mini"
    GPTO3_Mini = "o3-mini"
    Deepseek_R1 = "DeepSeek-R1"

class AssessmentType(str, Enum):
    PredefinedScore = "predefined_score"
    OnlineBackgroundCheck = "online_background_check"

class DocumentType(str, Enum):
    KTP = "KTP"
    KK = "KK"
    Ijazah = "Ijazah"
    BukuTabungan = "Buku Tabungan"
    NPWP = "NPWP"
    SignedOfferLetter = "Signed Offer Letter"