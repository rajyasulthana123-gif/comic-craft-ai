from app.schemas import (
    ComicLayoutPanel,
    ComicStory,
)


def build_comic_layout(
    story: ComicStory,
) -> list[ComicLayoutPanel]:

    layout = []

    for panel in story.panels:

        layout.append(
            ComicLayoutPanel(
                panel_number=panel.panel_number,
                title=panel.title,
                image_path=panel.image_path,
                scene_description=panel.scene_description,
                caption=panel.caption,
                narration=panel.narration,
                dialogue=panel.dialogue,
                image_prompt=panel.image_prompt,
            )
        )

    return layout