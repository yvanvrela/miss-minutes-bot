from database.config.db import engine, trackeds
from database.schemas.users_schema import UserSchema
from sqlalchemy import engine


class UsersRepository():
    def __init__(self, engine: engine) -> None:
        self.engine = engine

    def add_user(self, user: UserSchema) -> None:
        user_db = trackeds.insert().values(
            id_telegram=user.id_telegram,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            full_name=user.full_name,
            is_bot=user.is_bot
        )
        conn = self.engine.connect()
        conn.execute(user_db)
        conn.commit()
        conn.close()
        return user_db
