from enum import Enum, unique, auto


@unique
class AppEnv(str, Enum):
    DEV = auto()
    PROD = auto()
    TEST = auto()
