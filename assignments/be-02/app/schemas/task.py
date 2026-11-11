"""Validation for the task API."""
from pydantic import BaseModel, ConfigDict, StrictBool, field_validator, model_validator


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, value):
        if not value:
            raise ValueError("Title must not be empty")
        return value


class TaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str | None = None
    done: StrictBool | None = None

    @model_validator(mode="after")
    def valid_changes(self):
        if not self.model_fields_set or any(getattr(self, key) is None for key in self.model_fields_set):
            raise ValueError("Provide at least one non-null field")
        if self.title is not None and not self.title:
            raise ValueError("Title must not be empty")
        return self
