from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass
from itertools import islice
from typing import Generic, TypeVar


T = TypeVar("T")
Item = TypeVar("Item", covariant=True)
WrappedIter = TypeVar("WrappedIter", bound=AsyncIterator | Iterator, covariant=True)


@dataclass(frozen=True)
class batched(Generic[WrappedIter]):
    """
    Universal batching wrapper for sync and async iterators.
    """

    _iterator: WrappedIter
    batch_size: int = 100

    def __post_init__(self) -> None:
        if self.batch_size <= 1:
            raise ValueError(f"'batch_size' must be greater than 1 (got {self.batch_size})")

    def __aiter__(self: batched[AsyncIterator[Item]]) -> batched[AsyncIterator[Item]]:
        return self

    async def __anext__(self: batched[AsyncIterator[Item]]) -> list[Item]:
        bucket = []
        for _ in range(self.batch_size):
            try:
                item = await anext(self._iterator)
            except StopAsyncIteration:
                break
            else:
                bucket.append(item)

        if not bucket:
            raise StopAsyncIteration

        return bucket

    def __iter__(self: batched[Iterator[Item]]) -> batched[Iterator[Item]]:
        return self

    def __next__(self: batched[Iterator[Item]]) -> list[Item]:
        batch = list(islice(self._iterator, self.batch_size))
        if not batch:
            raise StopIteration
        return batch
