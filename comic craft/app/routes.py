import traceback

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.schemas import PromptRequest
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf


router = APIRouter()


def _templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


def _generate(request_data: PromptRequest):
    # Step 1: Generate comic outline
    outline = generate_outline(request_data)

    # Step 2: Generate complete comic story
    story = generate_story(
        request_data,
        outline,
    )

    # Step 3: Generate images for every panel
    for panel in story.panels:
        panel.image_path = generate_image(
            panel.image_prompt,
            panel.panel_number,
        )

    # Step 4: Build comic layout
    layout = build_comic_layout(story)

    # Step 5: Export comic as PDF
    pdf_path = save_pdf(
        layout,
        story.title,
    )

    return story, layout, pdf_path


# ========================================
# HOME PAGE
# ========================================

@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):
    return _templates(request).TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None,
        },
    )


# ========================================
# WEB FORM GENERATION
# ========================================

@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        settings = get_settings()

        data = PromptRequest(
            story_prompt=story_prompt[
                :settings.max_prompt_length
            ],
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        story, layout, pdf_path = _generate(data)

        return _templates(request).TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "story": story,
                "layout": layout,
                "pdf_path": pdf_path,
            },
        )

    except Exception as exc:
        print("\n")
        print("========================================")
        print("         COMIC GENERATION ERROR")
        print("========================================")
        print(f"ERROR: {exc}")
        print("\nFULL TRACEBACK:")
        traceback.print_exc()
        print("========================================")
        print("\n")

        return _templates(request).TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc),
            },
            status_code=500,
        )


# ========================================
# JSON API
# ========================================

@router.post("/generate-comic/json")
async def generate_json(data: PromptRequest):
    try:
        story, layout, pdf_path = _generate(data)

        return {
            "title": story.title,
            "panels": [
                panel.model_dump()
                for panel in layout
            ],
            "pdf_path": pdf_path,
        }

    except Exception as exc:
        print("\n")
        print("========================================")
        print("       JSON GENERATION ERROR")
        print("========================================")
        print(f"ERROR: {exc}")
        traceback.print_exc()
        print("========================================")
        print("\n")

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ========================================
# EXPORT SUCCESS
# ========================================

@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
    pdf: str = "",
):
    return _templates(request).TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_path": pdf,
        },
    )


# ========================================
# IMAGE TEST
# ========================================

@router.get(
    "/test-image",
    response_class=HTMLResponse,
)
async def test_image(
    request: Request,
    prompt: str = (
        "a cute fox in an enchanted forest, "
        "colorful comic book art"
    ),
):
    try:
        path = generate_image(
            prompt,
            999,
        )

        return _templates(request).TemplateResponse(
            request=request,
            name="image_test.html",
            context={
                "image_path": path,
                "prompt": prompt,
                "error": None,
            },
        )

    except Exception as exc:
        print("\n")
        print("========================================")
        print("          IMAGE TEST ERROR")
        print("========================================")
        print(f"ERROR: {exc}")
        traceback.print_exc()
        print("========================================")
        print("\n")

        return _templates(request).TemplateResponse(
            request=request,
            name="image_test.html",
            context={
                "image_path": None,
                "prompt": prompt,
                "error": str(exc),
            },
            status_code=500,
        )

