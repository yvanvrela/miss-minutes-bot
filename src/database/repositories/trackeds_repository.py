import datetime
from database.config.db import engine, trackeds
from database.schemas.trackeds_schema import TrackedSchema
from sqlalchemy import engine, desc, and_
from typing import List
from sqlalchemy.sql.expression import update


class TrackedsRepository():
    def __init__(self, engine: engine) -> None:
        self.engine = engine

    def add_track_time(self, tracked: TrackedSchema) -> None:
        tracked_db = trackeds.insert().values(
            start_time=tracked.start_time,
            stop_time=tracked.stop_time,
            time_worked=tracked.time_worked,
            task_id=tracked.task_id,
            task_name=tracked.task_name,
            task_description=tracked.task_description,
            date=tracked.date,
            user_id=tracked.user_id
        )
        conn = self.engine.connect()
        conn.execute(tracked_db)
        conn.commit()
        conn.close()
        return tracked_db

    def update_track_time(self, tracked: TrackedSchema) -> None:

        conn = self.engine.connect()

        last_tacking_id = self.get_last_tracking_id(tracked.user_id)

        update_st = update(trackeds).where(
            trackeds.c.id == last_tacking_id).values(
            task_description=tracked.task_description,
            stop_time=tracked.stop_time,
            time_worked=tracked.time_worked,
        )

        conn.execute(update_st)
        conn.commit()

        conn.close()

    def get_last_tracking_id(self, user_id: int) -> int:
        conn = self.engine.connect()

        statement = trackeds.select().where(
            trackeds.c.user_id == user_id).order_by(desc(trackeds.c.id))

        last_tacking_id = conn.execute(statement).fetchone()[0]

        return last_tacking_id

    def get_last_start_time(self, user_id: int) -> datetime.datetime:
        last_tacking_id = self.get_last_tracking_id(user_id)

        conn = self.engine.connect()
        statement = trackeds.select().where(
            trackeds.c.id == last_tacking_id)

        last_start_time = conn.execute(statement).fetchone()[1]

        return last_start_time

    def get_last_task_name(self, user_id: int) -> str:
        last_tacking_id = self.get_last_tracking_id(user_id)

        conn = self.engine.connect()
        statement = trackeds.select().where(
            trackeds.c.id == last_tacking_id)

        last_task_name = conn.execute(statement).fetchone()[5]

        return last_task_name

    def get_last_clickup_task_id(self, user_id: int) -> str:
        last_tacking_id = self.get_last_tracking_id(user_id)

        conn = self.engine.connect()
        statement = trackeds.select().where(
            trackeds.c.id == last_tacking_id)

        clickup_task_id = conn.execute(statement).fetchone()[4]

        return clickup_task_id

    def get_last_stop_time(self, user_id: int) -> datetime.datetime:
        last_tacking_id = self.get_last_tracking_id(user_id)

        conn = self.engine.connect()
        statement = trackeds.select().where(
            trackeds.c.id == last_tacking_id)

        last_stop_time = conn.execute(statement).fetchone()[2]

        return last_stop_time

    def get_tasks(self, user_id: int) -> list:
        conn = self.engine.connect()
        statement = trackeds.select().where(trackeds.c.user_id == user_id)
        trackeds_db = conn.execute(statement).fetchall()

        return trackeds_db

    def get_tasks_by_date(self, user_id: int, date: datetime.datetime) -> List[TrackedSchema]:
        conn = self.engine.connect()
        statement = trackeds.select().where(
            and_(trackeds.c.user_id == user_id, trackeds.c.date == date))
        trackeds_db = conn.execute(statement).fetchall()

        return trackeds_db

    def get_task_by_clickup_task_id(self, user_id: int, task_id: str) -> TrackedSchema:
        conn = self.engine.connect()
        statement = trackeds.select().where(
            and_(trackeds.c.user_id == user_id, trackeds.c.task_id == task_id))
        tracked_db = conn.execute(statement).fetchone()

        return tracked_db

    def delete_task_by_tracked_id(self, tracked_id: int):
        conn = self.engine.connect()
        statement = trackeds.delete().where(trackeds.c.id == tracked_id)
        conn.execute(statement)
        conn.commit()

        return True
