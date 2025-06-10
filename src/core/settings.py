
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    HOST: str
    PORT: int
    USERNAME: str
    PASSWORD: str
    NAME: str

    @property
    def db_url(self) -> str:
        return f"postgresql://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"


class Settings(BaseSettings):
    DB: DatabaseConfig

    class Config:
        case_sensitive = True
        env_nested_delimiter = "__"
        env_file = ".env"
        extra = "ignore"

def get_settings() -> Settings:
    return Settings()
