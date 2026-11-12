from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str
    cors_origins: str = "http://localhost:5173"
    debug: bool = False
    api_port: int = 9000
    
    model_config = {"env_file": ".env"}
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()  # type: ignore[call-arg]
