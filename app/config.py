from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/inventar_db"
    secret_key: str = "dev-secret-key"
    debug: bool = True
    app_name: str = "Veranstaltungstechnik Inventar"

    class Config:
        env_file = ".env"


settings = Settings()
