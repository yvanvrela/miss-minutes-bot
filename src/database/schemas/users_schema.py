from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    id_telegram: int = Field()
    first_name: str = Field()
    last_name: str = Field()
    full_name: str = Field()
    username: str | None = Field()
    is_bot: bool = Field()
    clickup_user_id: str | None = Field()
    clickup_access_token: str | None = Field()
