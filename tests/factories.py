"""Define the factories for the test models."""

from typing import Any, Dict, List, Tuple

import factory
from faker import Faker

from .model import User


class UserFactory(factory.Factory):  # type: ignore
    """Generate a fake user."""

    id_ = factory.Faker("pyint")
    name = factory.Faker("name")
    bio = factory.Faker("sentence")

    class Meta:
        """Configure factoryboy class."""

        model = User


def create_list_data() -> Tuple[List[Any], List[str]]:
    """Create fake list data."""
    faker = Faker()

    number_columns = faker.pyint(min_value=1, max_value=10)
    number_rows = faker.pyint(min_value=3, max_value=100)
    data = [
        faker.pylist(number_columns, variable_nb_elements=False, value_types=[str])
        for _ in range(0, number_rows)
    ]
    header = faker.pylist(number_columns, variable_nb_elements=False, value_types=[str])
    return data, header


def create_dict_data() -> List[Dict[str, str]]:
    """Create fake dict data."""
    faker = Faker()

    keys = faker.pylist(10, variable_nb_elements=True, value_types=[str])

    data = []
    for _ in range(0, faker.pyint(min_value=3, max_value=100)):
        row = {}
        for key in keys:
            row[key] = faker.word()
        data.append(row)

    return data
