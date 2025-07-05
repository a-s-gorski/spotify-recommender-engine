from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tokenizer_path: str
    qdrant_url: str
    qdrant__service__api__key: str
    qdrant_collection_name: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
