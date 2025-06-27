from __future__ import annotations

from typing import Generic, TypeVar, Hashable, Iterable
K = TypeVar('K', bound=Hashable)
V = TypeVar('V', bound=Hashable)


class BiMap(Generic[K, V]):
    def __init__(self) -> None:
        self._key_to_values: dict[K, set[V]] = {}
        self._value_to_keys: dict[V, set[K]] = {}

    def add_key_value(self, key: K, value: V) -> None:
        if (value_set := self._key_to_values.get(key)) is not None:
            value_set.add(value)
        else:
            self._key_to_values[key] = {value}

        if (key_set := self._value_to_keys.get(value)) is not None:
            key_set.add(key)
        else:
            self._value_to_keys[value] = {key}

    def discard_key_value(self, key: K, value: V) -> None:
        value_set = self._key_to_values.get(key)
        key_set = self._value_to_keys.get(value)
        if value_set is not None and key_set is not None:
            value_set.discard(value)
            key_set.discard(key)

    def contains_key_value(self, key: K, value: V) -> bool:
        if (value_set := self._key_to_values.get(key)) is None:
            return False
        if (key_set := self._value_to_keys.get(value)) is None:
            return False
        return value in value_set and key in key_set

    def update(self, other: BiMap[K, V]) -> None:
        for key, other_value_set in other._key_to_values.items():
            if (value_set := self._key_to_values.get(key)) is not None:
                value_set.update(other_value_set)
            else:
                self._key_to_values[key] = other_value_set.copy()

        for value, other_key_set in other._value_to_keys.items():
            if (key_set := self._value_to_keys.get(value)) is not None:
                key_set.update(other_key_set)
            else:
                self._value_to_keys[value] = other_key_set.copy()

    def difference_update(self, other: BiMap[K, V]) -> None:
        for key, other_value_set in other._key_to_values.items():
            if (value_set := self._key_to_values.get(key)) is not None:
                value_set.difference_update(other_value_set)

        for value, other_key_set in other._value_to_keys.items():
            if (key_set := self._value_to_keys.get(value)) is not None:
                key_set.difference_update(other_key_set)

    def get_keys(self, value: V) -> set[K]:
        if (key_set := self._value_to_keys.get(value)) is None:
            return ()
        return key_set

    def get_values(self, key: K) -> set[V]:
        if (value_set := self._key_to_values.get(key)) is None:
            return ()
        return value_set

    def keys(self) -> Iterable[K]:
        return self._key_to_values.keys()

    def values(self) -> Iterable[V]:
        return self._value_to_keys.keys()
