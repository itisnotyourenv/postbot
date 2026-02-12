from enum import StrEnum

from src.domain.common.vo.string import NonEmptyString


class UniqueKey(NonEmptyString):
    min_length = 8
    max_length = 8


class ContentType(StrEnum):
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    GIF = "gif"


class PostStatus(StrEnum):
    ACTIVE = "active"
    DELETED = "deleted"


class ButtonStyle(StrEnum):
    DEFAULT = "default"
    GREEN = "green"
    BLUE = "blue"
    RED = "red"


class TextMd(NonEmptyString):
    min_length = 1
    max_length = 1024


class TelegramFileId(NonEmptyString):
    min_length = 1
    max_length = 512
