from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_premium: bool = False
    is_banned: bool = False
    premium_expiry: Optional[datetime] = None
    jio_phone: Optional[str] = None
    jio_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

class PremiumRecord(BaseModel):
    user_id: int
    granted_by: int
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    is_permanent: bool = False
    duration_days: Optional[int] = None

class BannedUser(BaseModel):
    user_id: int
    banned_by: int
    reason: Optional[str] = None
    banned_at: datetime = Field(default_factory=datetime.utcnow)

class Config(BaseModel):
    key: str
    value: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Recording(BaseModel):
    recording_id: str
    user_id: int
    channel_id: str
    channel_name: str
    start_time: datetime
    end_time: datetime
    status: str  # 'recording', 'processing', 'completed', 'failed'
    output_file: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    message_id: Optional[int] = None
