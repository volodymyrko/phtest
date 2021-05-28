from datetime import date
from typing import Optional

from pydantic import BaseModel, PositiveInt, constr


class PostAnnouncementModel(BaseModel):
    """Validate data to POST /announcements."""
    name: constr(min_length=2, max_length=100)
    description: constr(min_length=2, max_length=500)
    date: date


class GetAllAnnouncementsModel(BaseModel):
    """Validate queryset to GET /announcements."""
    limit: Optional[PositiveInt]
    last_evaluated_key: Optional[str]
