from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):

    story_prompt: str = Field(
        min_length=5,
        max_length=1200,
    )

    character_name: str = Field(
        min_length=1,
        max_length=80,
    )

    setting: str = Field(
        min_length=1,
        max_length=120,
    )

    tone: str = Field(
        min_length=1,
        max_length=50,
    )

    art_style: str = Field(
        min_length=1,
        max_length=80,
    )

    @field_validator(
        "story_prompt",
        "character_name",
        "setting",
        "tone",
        "art_style",
    )
    @classmethod
    def strip_values(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty.")

        return value


class PanelOutline(BaseModel):

    panel_number: int

    title: str

    scene_description: str

    image_prompt: str


class ComicOutline(BaseModel):

    panels: list[PanelOutline]


class ComicPanel(BaseModel):

    panel_number: int

    title: str

    scene_description: str

    caption: str

    narration: str

    dialogue: str

    image_prompt: str

    image_path: str = ""


class ComicStory(BaseModel):

    title: str

    panels: list[ComicPanel]


class ComicLayoutPanel(BaseModel):

    panel_number: int

    title: str

    image_path: str

    scene_description: str

    caption: str

    narration: str

    dialogue: str

    image_prompt: str