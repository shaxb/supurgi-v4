from pydantic import BaseModel, Field
import datetime

class TickData(BaseModel):
    time: int = Field(..., description="Time of the last quote (seconds since epoch)")
    bid: float = Field(..., description="Current Bid price")
    ask: float = Field(..., description="Current Ask price")
    last: float = Field(..., description="Price of the last deal") # Note: May be 0 if no deals
    volume: int = Field(..., description="Volume for the last deal") # Note: May be 0 if no deals
    time_msc: int = Field(..., description="Time of the last quote in milliseconds since epoch")
    flags: int = Field(..., description="Tick flags")
    volume_real: float = Field(..., description="Volume for the last deal with greater accuracy")

    class Config:
        from_attributes = True  # Changed from 'orm_mode = True'