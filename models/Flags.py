from enum import Enum, auto


class AutoName(Enum):
    def _generate_next_value_(name: str, start, count, last_values):
        return name.lower()


class Action(AutoName):
    COPY = auto()


class Env(AutoName):
    PROD = auto()
    DEV = auto()
    ALL = auto()
    LOCAL = auto()
