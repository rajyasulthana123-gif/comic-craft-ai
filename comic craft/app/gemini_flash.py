from google.genai import types
from app.config import get_settings
from app.gemini_client import get_gemini_client
from app.schemas import ComicOutline, PromptRequest


def generate_outline(
    request: PromptRequest,
) -> ComicOutline:

    settings = get_settings()

    client = get_gemini_client()

    prompt = f"""
Create a cohesive 5-panel comic outline.

User story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:

- Exactly 5 panels.
- Preserve the same main character throughout.
- Preserve the setting.
- Make each panel continue the story.
- Give every panel a clear visual scene.
- Create useful image prompts.
- Do not put dialogue inside image_prompt.
- Keep the story family-friendly.
- Avoid explicit or graphic content.
"""

    response = client.models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ComicOutline,
            temperature=0.9,
        ),
    )

    if getattr(response, "parsed", None):

        outline = response.parsed

    else:

        outline = ComicOutline.model_validate_json(
            response.text
        )

    if len(outline.panels) != 5:

        raise RuntimeError(
            f"Gemini returned {len(outline.panels)} panels. "
            "Expected exactly 5."
        )

    return outline