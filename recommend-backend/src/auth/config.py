from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str

    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()