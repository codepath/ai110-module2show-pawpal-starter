"""Shared fixtures: real PawPal+ objects only — no mocks (see ADR-0004)."""

from datetime import date

import pytest

from pawpal_system import Owner, Pet, Task


@pytest.fixture
def owner_with_two_pets() -> Owner:
    """An Owner with two pets and no tasks yet."""
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog"))
    owner.add_pet(Pet(name="Whiskers", species="cat"))
    return owner


def make_task(description: str, time: str, **kwargs) -> Task:
    """A Task due today unless overridden."""
    return Task(
        description=description,
        time=time,
        date=kwargs.pop("date", date.today()),
        **kwargs
    )
