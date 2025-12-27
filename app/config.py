# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # LLM / embeddings
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    gemini_model_name: str = Field(...,alias="GEMINI_MODEL_NAME")

    # Tavily
    tavily_api_key: str = Field(..., alias="TAVILY_API_KEY")

    # GCP
    # gcp_project_id: str = Field(..., alias="GCP_PROJECT_ID")
    # gcp_region: str = Field(..., alias="GCP_REGION")
    # gcs_bucket_name: str = Field(..., alias="GCS_BUCKET_NAME")

    # Chroma
    chroma_persist_dir: str = Field(alias="CHROMA_PERSIST_DIR")

    # Flask
    flask_debug: bool = Field(default=False)
    flask_host: str = Field(default="0.0.0.0")
    flask_port: int = Field(default=5000)
    api_base:str = Field(alias="API_BASE")

    # Gradio
    gradio_host: str = Field(default="0.0.0.0")
    gradio_port: int = Field(default=8080)
    

    # Misc
    environment: str = Field(default="dev")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
