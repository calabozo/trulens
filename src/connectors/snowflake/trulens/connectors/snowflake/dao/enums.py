from enum import Enum


# snowflake object type
class ObjectType(str, Enum):
    EXTERNAL_AGENT = "EXTERNAL AGENT"

    @classmethod
    def is_valid_object(cls, key) -> bool:
        return key in cls.__members__.values()
