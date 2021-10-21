"""Store the classes and fixtures used throughout the tests."""

from random import SystemRandom
from typing import Any, Dict, List, Tuple

import pytest
from pydantic import BaseModel  # noqa: E0611

from . import factories


@pytest.fixture(scope="session", autouse=True)
def faker_seed() -> int:
    """Create a random seed for the Faker library."""
    return SystemRandom().randint(0, 999999)


ListData = Tuple[List[List[Any]], List[str]]
DictData = List[Dict[str, str]]
PydanticData = List[BaseModel]


@pytest.fixture(name="pydantic_data")
def pydantic_data_() -> PydanticData:
    """Return a list of pydantic objects."""
    return factories.UserFactory.create_batch(10)


@pytest.fixture(name="list_data")
def list_data_() -> ListData:
    """Return a list of pydantic objects."""
    return factories.create_list_data()


@pytest.fixture(name="dict_data")
def dict_data_() -> DictData:
    """Return a list of pydantic objects."""
    return factories.create_dict_data()
