from typing import Protocol, Callable


class SupportsReading(Protocol):
    read: Callable[..., bytes]
