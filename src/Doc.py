import re
import pydantic
from typing import Optional
from typing import Any
from src.Entity import Entity


class Doc(pydantic.BaseModel):
    text: str
    raw_text: Optional[str] = None
    entities: list[Entity] = []
    entity_pattern: str = r"\[\w+\]\(\w+\)"

    def model_post_init(self, __context: Any) -> Entity:
        self.raw_text = self.text
        self.text = "".join(re.split(r"\[(\w+)\]\(\w+\)", self.raw_text))
        self.get_entities()

    def get_entities(self) -> list[Entity]:
        raw_text = self.raw_text
        entity = re.search(self.entity_pattern, raw_text)
        while entity:
            entity_text = entity.group()
            entity_value = re.search(r"\[\w+\]", entity_text).group()[1:-1]
            entity_name = re.search(r"\(\w+\)", entity_text).group()[1:-1]
            raw_text = raw_text.replace(entity_text, entity_value, 1)
            self.entities.append(
                Entity(
                    name=entity_name,
                    value=entity_value,
                    start=entity.start(),
                    end=entity.start() + len(entity_value),
                )
            )
            entity = re.search(self.entity_pattern, raw_text)
        self.text = raw_text
        return self.entities
