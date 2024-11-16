from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """Base schema with common configurations"""
    model_config = ConfigDict(from_attributes=True)
