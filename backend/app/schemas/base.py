from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        extra='forbid'
    )

class TimestampSchema(BaseSchema):
    """Schema with timestamp fields"""
    created_at: datetime
    updated_at: datetime

class BaseResponseSchema(TimestampSchema):
    """Base schema for responses with ID"""
    id: int