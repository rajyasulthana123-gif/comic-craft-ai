from pathlib import Path
import re
import uuid

from PIL import Image, ImageDraw

from app.config import get_settings


BASE_DIR = Path(__file__).resolve().parent.parent

PANELS_DIR = (
    BASE_DIR /
    "static" /
    "panels"
)


_pipeline = None


def _safe_filename(text: str) -> str:

    cleaned = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "-",
        text,
    )

    cleaned = cleaned.strip("-").lower()

    if not cleaned:
        cleaned = "panel"

    return (
        cleaned[:50]
        + "-"
        + uuid.uuid4().hex[:8]
        + ".png"
    )


def _get_device():

    import torch

    settings = get_settings()

    if settings.image_device == "cuda":
        return "cuda"

    if settings.image_device == "cpu":
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


def _load_pipeline():

    global _pipeline

    if _pipeline is not None:
        return _pipeline

    import torch

    from diffusers import (
        StableDiffusionPipeline
    )

    settings = get_settings()

    device = _get_device()

    if device == "cuda":

        dtype = torch.float16

    else:

        dtype = torch.float32

    _pipeline = StableDiffusionPipeline.from_pretrained(
        settings.image_model_id,
        torch_dtype=dtype,
    )

    _pipeline = _pipeline.to(device)

    return _pipeline


def _placeholder_image(
    prompt: str,
    output_path: Path,
):

    settings = get_settings()

    image = Image.new(
        "RGB",
        (
            settings.image_width,
            settings.image_height,
        ),
        "white",
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (
            10,
            10,
            settings.image_width - 10,
            settings.image_height - 10,
        ),
        outline="black",
        width=4,
    )

    draw.text(
        (30, 30),
        "ComicCraft",
        fill="black",
    )

    wrapped_lines = []

    for i in range(
        0,
        min(len(prompt), 700),
        45,
    ):

        wrapped_lines.append(
            prompt[i:i + 45]
        )

    wrapped = "\n".join(
        wrapped_lines
    )

    draw.text(
        (30, 90),
        wrapped,
        fill="black",
        spacing=8,
    )

    image.save(
        output_path,
        format="PNG",
    )


def generate_image(
    image_prompt: str,
    panel_number: int,
) -> str:

    settings = get_settings()

    PANELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = _safe_filename(
        f"panel-{panel_number}"
    )

    output_path = (
        PANELS_DIR /
        filename
    )

    # -------------------------
    # Development mode
    # -------------------------

    if (
        settings.image_provider.lower()
        == "placeholder"
    ):

        _placeholder_image(
            image_prompt,
            output_path,
        )

        return (
            f"/static/panels/{filename}"
        )

    # -------------------------
    # Stable Diffusion
    # -------------------------

    try:

        pipe = _load_pipeline()

        result = pipe(
            prompt=image_prompt,
            num_inference_steps=settings.image_steps,
            width=settings.image_width,
            height=settings.image_height,
        )

        image = result.images[0]

        image.save(
            output_path
        )

        return (
            f"/static/panels/{filename}"
        )

    except Exception as exc:

        # Keep the application running
        # even if the local model fails.

        _placeholder_image(
            f"Image generation failed:\n{exc}",
            output_path,
        )

        return (
            f"/static/panels/{filename}"
        )