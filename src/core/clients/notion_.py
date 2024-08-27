import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()


class NotionClient:
    def __init__(self):
        """Initialize the Notion client with an integration token."""
        self.client = Client(auth=os.getenv("NOTION_API_KEY"))

    def create_page(self, parent_id: str, title: str, markdown_content: str) -> dict:
        """Create a new page in Notion with the provided markdown content."""
        blocks = self._convert_markdown_to_blocks(markdown_content)

        new_page = self.client.pages.create(
            parent={"database_id": parent_id},  # or "page_id" for a regular page
            properties={"title": [{"type": "text", "text": {"content": title}}]},
            children=blocks,
        )

        return new_page

    def _convert_markdown_to_blocks(self, markdown_content: str) -> list:
        """Convert markdown content into Notion blocks."""
        lines = markdown_content.split("\n")
        blocks = []

        for line in lines:
            if line.startswith("# "):
                blocks.append(self._create_heading_block(line[2:], level=1))
            elif line.startswith("## "):
                blocks.append(self._create_heading_block(line[3:], level=2))
            elif line.startswith("### "):
                blocks.append(self._create_heading_block(line[4:], level=3))
            elif line.startswith("- "):
                blocks.append(self._create_bulleted_list_item_block(line[2:]))
            else:
                blocks.append(self._create_paragraph_block(line))

        return blocks

    def _create_heading_block(self, content: str, level: int) -> dict:
        """Create a heading block in Notion."""
        return {
            "object": "block",
            "type": f"heading_{level}",
            f"heading_{level}": {"rich_text": [self._create_rich_text_object(content)]},
        }

    def _create_paragraph_block(self, content: str) -> dict:
        """Create a paragraph block in Notion."""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [self._create_rich_text_object(content)]},
        }

    def _create_bulleted_list_item_block(self, content: str) -> dict:
        """Create a bulleted list item block in Notion."""
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [self._create_rich_text_object(content)]
            },
        }

    def _create_rich_text_object(self, content: str) -> dict:
        """Create a rich text object with optional annotations."""
        # This example assumes no annotations, but you can extend this logic to detect markdown annotations
        annotations = {
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": "default",
        }

        # Detect markdown syntax for bold, italic, etc., and set annotations accordingly
        if "**" in content:
            content = content.replace("**", "")
            annotations["bold"] = True
        if "_" in content:
            content = content.replace("_", "")
            annotations["italic"] = True
        if "`" in content:
            content = content.replace("`", "")
            annotations["code"] = True

        # Basic link detection (e.g., [text](url))
        link = None
        if "[" in content and "](" in content:
            start = content.index("[") + 1
            end = content.index("]")
            link_start = content.index("](") + 2
            link_end = content.index(")", link_start)
            text = content[start:end]
            link = content[link_start:link_end]
            content = text

        return {
            "type": "text",
            "text": {"content": content, "link": {"url": link} if link else None},
            "annotations": annotations,
            "plain_text": content,
            "href": link,
        }
