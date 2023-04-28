from typing import Protocol, Awaitable


class SupportsReading(Protocol):
    def read(self, *args, **kwargs) -> bytes:
        pass


class SupportsAsyncReading(Protocol):
    def read(self, *args, **kwargs) -> Awaitable[bytes]:
        pass
