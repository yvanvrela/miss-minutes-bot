from pydantic import BaseModel, Field
import datetime


class TrackedSchema(BaseModel):
    start_time: datetime.datetime | None = Field()
    stop_time:  datetime.datetime | None = Field()
    time_worked: float | None = Field()
    task_id: str | None = Field()
    task_name: str = Field()
    task_description: str | None = Field()
    date:  datetime.date | None = Field()
    user_id: int = Field()
