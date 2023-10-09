from pydantic import BaseModel


class AlarmData(BaseModel):
    user_id: int
    items: list
