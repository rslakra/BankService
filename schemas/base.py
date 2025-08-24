from typing import List

from pydantic import BaseModel


# Base schemas
class BaseSchema(BaseModel):
    """Base schema for all schemas"""

    class Config:
        from_attributes = True


# Error schemas
class ErrorResponse(BaseSchema):
    detail: str


class ValidationErrorResponse(BaseSchema):
    detail: List[dict]
