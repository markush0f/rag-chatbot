import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Crecenia Chatbot")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "markus")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "1234")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "Crecenia_chatbot")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    DB_LOGS: bool = os.getenv("DB_LOGS", False)
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
