from pathlib import Path
import re
import uuid

from fpdf import FPDF
from PIL import Image

from app.schemas import ComicLayoutPanel


BASE_DIR = Path(__file__).resolve().parent.parent

EXPORTS_DIR = (
    BASE_DIR /
    "static" /
    "exports"
)


def _local_image_path(
    image_path: str,
) -> Path:

    relative = image_path.replace(
        "/static/",
        "",
        1,
    )

    return (
        BASE_DIR /
        "static" /
        relative
    )


def _clean_text(
    value: str,
) -> str:

    return (
        value
        .encode(
            "latin-1",
            "replace",
        )
        .decode("latin-1")
    )


def save_pdf(
    layout: list[ComicLayoutPanel],
    title: str,
) -> str:

    EXPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "-",
        title,
    )

    filename = filename.strip("-")

    if not filename:
        filename = "comic"

    filename = (
        filename[:50]
        + "-"
        + uuid.uuid4().hex[:8]
        + ".pdf"
    )

    output_path = (
        EXPORTS_DIR /
        filename
    )

    pdf = FPDF(
        "P",
        "mm",
        "A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in layout:

        pdf.add_page()

        # -------------------------
        # Panel title
        # -------------------------

        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        pdf.multi_cell(
            0,
            10,
            _clean_text(
                f"Panel {panel.panel_number}: "
                f"{panel.title}"
            ),
        )

        # -------------------------
        # Image
        # -------------------------

        image_path = _local_image_path(
            panel.image_path
        )

        if image_path.exists():

            with Image.open(
                image_path
            ) as image:

                width, height = (
                    image.size
                )

            max_width = 180
            max_height = 115

            ratio = min(
                max_width / width,
                max_height / height,
            )

            display_width = (
                width * ratio
            )

            display_height = (
                height * ratio
            )

            pdf.image(
                str(image_path),
                x=15,
                y=32,
                w=display_width,
                h=display_height,
            )

            pdf.ln(
                display_height + 6
            )

        # -------------------------
        # Scene
        # -------------------------

        pdf.set_font(
            "Helvetica",
            "I",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            _clean_text(
                panel.scene_description
            ),
        )

        pdf.ln(2)

        # -------------------------
        # Caption
        # -------------------------

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            "Caption",
        )

        pdf.set_font(
            "Helvetica",
            "",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            _clean_text(
                panel.caption
            ),
        )

        pdf.ln(1)

        # -------------------------
        # Narration
        # -------------------------

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            "Narration",
        )

        pdf.set_font(
            "Helvetica",
            "",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            _clean_text(
                panel.narration
            ),
        )

        # -------------------------
        # Dialogue
        # -------------------------

        if panel.dialogue:

            pdf.ln(1)

            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.multi_cell(
                0,
                7,
                "Dialogue",
            )

            pdf.set_font(
                "Helvetica",
                "",
                11,
            )

            pdf.multi_cell(
                0,
                7,
                _clean_text(
                    panel.dialogue
                ),
            )

    pdf.output(
        str(output_path)
    )

    return (
        f"/static/exports/{filename}"
    )