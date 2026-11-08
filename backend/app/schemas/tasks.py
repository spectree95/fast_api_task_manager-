from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StringConstraints, field_validator


TaskTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
TaskDescription = Annotated[str, StringConstraints(max_length=1000)]
SearchQuery = Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: TaskTitle
    description: TaskDescription = ""


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int


class TaskListResponce(BaseModel):
    items: list[TaskResponse]
    total: int
    skip: int
    limit: int


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: TaskTitle | None = None
    description: TaskDescription | None = None
    completed: StrictBool | None = None

    @field_validator("title", "description", "completed", mode="before")
    @classmethod
    def reject_explicit_null(cls, value):
        # Omitted fields keep their defaults and are excluded from PATCH data.
        if value is None:
            raise ValueError("Omit unchanged fields instead of setting them to null.")
        return value


class SortField(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    title = "title"


class OrderField(str, Enum):
    asc = "asc"
    desc = "desc"


class TaskFilter(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    completed: bool | None = None
    sort: SortField = SortField.created_at
    order: OrderField = OrderField.desc
    q: SearchQuery = Field("", description="Search titles and descriptions by literal text, ignoring case.")
