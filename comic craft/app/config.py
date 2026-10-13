from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):   
     gemini_api_key: str ="AQ.Ab8RN6IvzOs3vo9dKGvSM24rD_xCsSOJrs4GFTZt5pP_NB9jhQ"



    gemini_outline_model: str = "gemini-2.5-flash"
    gemini_story_model: str = "gemini-3.1-flash-preview"
    huggingface_token: str = " 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"
    image_model: str = "stabilityai/stable-diffusion-xl-base-1.0"

    max_prompt_length: int = 2000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()