"""Define the models for the tests."""

from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """Define the example of a model."""

    id_: int = Field(0, title="ID")
    name: str = "Jane Doe"
    bio: Optional[str] = None
