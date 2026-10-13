from google.genai import types
from app.config import get_settings
from app.gemini_client import get_gemini_client
from app.schemas import (
    ComicOutline,
    ComicStory,
    PromptRequest,
)


def generate_story(
    request: PromptRequest,
    outline: ComicOutline,
) -> ComicStory:

    settings = get_settings()

    client = get_gemini_client()

    outline_text = outline.model_dump_json(
        indent=2
    )

    prompt = f"""
Expand the following comic outline into
a polished five-panel comic story.

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Original story idea:
{request.story_prompt}

Comic outline:

{outline_text}

For every panel provide:

- panel_number
- title
- scene_description
- caption
- narration
- dialogue
- image_prompt

Rules:

1. Exactly five panels.
2. Keep the same character throughout.
3. Keep visual continuity between panels.
4. Keep the same general art style.
5. Dialogue should sound natural.
6. Image prompts must describe visual elements only.
7. Keep the story family-friendly.
8. Do not create graphic or explicit content.
9. Create one short comic title.
"""

    response = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ComicStory,
            temperature=0.9,
        ),
    )

    if getattr(response, "parsed", None):

        story = response.parsed

    else:

        story = ComicStory.model_validate_json(
            response.text
        )

    if len(story.panels) != 5:

        raise RuntimeError(
            f"Gemini returned {len(story.panels)} panels. "
            "Expected exactly 5."
        )

    return story