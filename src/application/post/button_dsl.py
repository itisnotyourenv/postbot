import re
from dataclasses import dataclass
from urllib.parse import urlparse

from src.domain.post.vo import ButtonStyle


class ButtonDslError(Exception):
    pass


@dataclass
class ParsedButton:
    text: str
    url: str
    style: ButtonStyle


BUTTON_PATTERN = re.compile(r"\[([^\]]+)\]")
VALID_STYLES = {s.value for s in ButtonStyle}


def parse_buttons_dsl(raw: str) -> list[list[ParsedButton]]:
    """Parse DSL string into rows of buttons.

    Format: [Text + URL + color] per button.
    Each line is a new row.
    Color is optional, defaults to 'default'.

    Raises ButtonDslError on invalid input.
    """
    rows: list[list[ParsedButton]] = []

    for raw_line in raw.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue

        matches = BUTTON_PATTERN.findall(line)
        if not matches:
            msg = "Could not parse buttons. Example: [Text + https://url + green]"
            raise ButtonDslError(msg)

        row: list[ParsedButton] = []
        for match in matches:
            parts = [p.strip() for p in match.split("+")]

            if len(parts) < 2:
                msg = (
                    "Each button must have at least text and URL. "
                    "Example: [Text + https://url]"
                )
                raise ButtonDslError(msg)

            text = parts[0]
            url = parts[1]
            style_str = parts[2] if len(parts) >= 3 else "default"

            if not text:
                msg = "Button text cannot be empty."
                raise ButtonDslError(msg)

            _validate_url(url, text)

            style_str = style_str.lower()
            if style_str not in VALID_STYLES:
                msg = f'Unknown color "{style_str}". Use: default, green, red.'
                raise ButtonDslError(msg)

            row.append(
                ParsedButton(
                    text=text,
                    url=url,
                    style=ButtonStyle(style_str),
                )
            )

        rows.append(row)

    return rows


def _validate_url(url: str, button_text: str) -> None:
    try:
        result = urlparse(url)
        if not result.scheme or not result.netloc:
            raise ValueError
    except (ValueError, AttributeError):
        msg = f'Invalid URL for button "{button_text}"'
        raise ButtonDslError(msg) from None
