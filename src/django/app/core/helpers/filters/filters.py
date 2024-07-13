"""
This module contains custom implementation of strawberry django graphql look up filters.

References:
    https://github.com/strawberry-graphql/strawberry-graphql-django/blob/8e4f506b80459fe99fe4188a0fc78890110758ee/strawberry_django/filters.py#L53C1-L53C1
"""
import strawberry
from strawberry import UNSET

from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar


T = TypeVar("T")


@strawberry.input
class TextFilterLookup(Generic[T]):
    exact: Optional[T] = UNSET
    i_exact: Optional[T] = UNSET
    contains: Optional[T] = UNSET
    i_contains: Optional[T] = UNSET
    in_list: Optional[List[T]] = UNSET
    starts_with: Optional[T] = UNSET
    i_starts_with: Optional[T] = UNSET
    ends_with: Optional[T] = UNSET
    i_ends_with: Optional[T] = UNSET
    regex: Optional[str] = UNSET
    i_regex: Optional[str] = UNSET
    n_exact: Optional[T] = UNSET
    n_i_exact: Optional[T] = UNSET
    n_contains: Optional[T] = UNSET
    n_i_contains: Optional[T] = UNSET
    n_in_list: Optional[List[T]] = UNSET
    n_starts_with: Optional[T] = UNSET
    n_i_starts_with: Optional[T] = UNSET
    n_ends_with: Optional[T] = UNSET
    n_i_ends_with: Optional[T] = UNSET
    n_range: Optional[List[T]] = UNSET
    n_regex: Optional[str] = UNSET
    n_i_regex: Optional[str] = UNSET


@strawberry.input
class NumericFilterLookup(Generic[T]):
    exact: Optional[T] = UNSET
    in_list: Optional[List[T]] = UNSET
    gt: Optional[T] = UNSET
    gte: Optional[T] = UNSET
    lt: Optional[T] = UNSET
    lte: Optional[T] = UNSET
    range: Optional[List[T]] = UNSET
    regex: Optional[str] = UNSET
