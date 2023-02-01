import datetime
from database.config.db import engine, trackeds
from database.schemas.trackeds_schema import TrackedSchema
from sqlalchemy import engine, desc
from sqlalchemy.sql.expression import update


class TrackedsRepository():
    def __init__(self, engine: engine) -> None:
        self.engine = engine

    def add_track_time(self, tracked: TrackedSchema) -> None:
        tracked_db = trackeds.insert().values(
            start_time=tracked.start_time,
            stop_time=tracked.stop_time,
            time_worked=tracked.time_worked,
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
            stop_time=tracked.stop_time,
            time_worked=tracked.time_worked,
        )

        conn.execute(update_st)
        conn.commit()

        conn.close()

        return 'hecho'

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

    def get_last_stop_time(self, user_id: int) -> datetime.datetime:
        last_tacking_id = self.get_last_tracking_id(user_id)

        conn = self.engine.connect()
        statement = trackeds.select().where(
            trackeds.c.id == last_tacking_id)

        last_stop_time = conn.execute(statement).fetchone()[2]

        return last_stop_time
