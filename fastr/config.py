from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the FastAPI app. Override with environment variables or .env file.

    Override example:
    `export FASTR_SECRET_KEY=secret`
    """

    database_url: str = "sqlite+aiosqlite:///"
    database_path: str = "fastr.sqlite"
    secret_key: str = "<override_in_production>"

    class Config:
        env_prefix = "fastr_"
        env_file = ".env"

    @property
    def connectstring(self):
        return self.database_url + self.database_path


settings = Settings()
