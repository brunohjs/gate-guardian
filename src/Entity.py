import pydantic


class Entity(pydantic.BaseModel):
    name: str
    value: str
    start: int
    end: int
