from pydantic import BaseModel, Field
import datetime


class TrackedSchema(BaseModel):
    start_time: datetime.datetime | None = Field()
    stop_time:  datetime.datetime | None = Field()
    time_worked: float | None = Field()
    task: str = Field()
    date:  datetime.date | None = Field()
    user_id: int = Field()
