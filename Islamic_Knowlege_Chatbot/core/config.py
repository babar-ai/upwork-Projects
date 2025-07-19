
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    VERSION: str = "1.3"
    LOGGING_DIR: str = "logs"
    LLM_MODEL: str = "gpt-4.1-nano"
    EMBEDDING_MODEL: str = "text-embedding-3-small"             #new added
    QURAN_COLLECTION_NAME: str = "quran_collection"
    HADITH_COLLECTION_NAME: str = "hadith_collection"
    TAFSEER_COLLECTION_NAME: str = "tafseer_collection"
    ISLAMIC_INFO_COLLECTION_NAME: str = "general_islamic_info"

    GROQ_API_KEY: str
    TAVILY_API_KEY: str
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    QURAN_QDRANT_URL: str
    HADITH_QDRANT_URL: str
    TAFSEER_QDRANT_URL: str
    QURAN_QDRANT_API_KEY: str
    HADITH_QDRANT_API_KEY: str
    TAFSEER_QDRANT_API_KEY: str
    GENERAL_ISLAMIC_INFO_URL: str
    GENERAL_ISLAMIC_INFO_KEY: str


    class Config:
        env_file = ".env"



settings = Settings()
