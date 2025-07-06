from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str
    mongo_db_name: str
    mongo_max_neightbors: int = 500

    class Config:
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
