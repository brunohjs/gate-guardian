import re
import pydantic
from src.Model import Model
from src.Entity import Entity
from pycpfcnpj import cpfcnpj


class PIIDetector(Model, pydantic.BaseModel):
    name: str = "pii_model"
    entities: dict[str, bool] | None = {
        "email": True,
        "person_name": True,
        "person_id": True
    }

    @staticmethod
    def person_id_checker(text: str) -> list[Entity]:
        regex = r"[\.\d/-]{11,}"
        result = []
        temp_text = text
        matched = re.search(regex, temp_text)
        while matched:
            if cpfcnpj.validate(matched.group()):
                result.append(
                    Entity(
                        name="PERSON_ID",
                        value=matched.group(),
                        start=matched.start(),
                        end=matched.end()
                    )
                )
            temp_text = temp_text[:matched.start()] + "" + temp_text[matched.end():]
            matched = re.search(regex, temp_text)
        return result

    @staticmethod
    def email_checker(text: str) -> list[Entity]:
        regex = r"[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}"
        result = []
        temp_text = text
        matched = re.search(regex, temp_text)
        while matched:
            result.append(
                Entity(
                    name="EMAIL_ADDRESS",
                    value=matched.group(),
                    start=matched.start(),
                    end=matched.end()
                )
            )
            temp_text = temp_text[:matched.start()] + "" + temp_text[matched.end():]
            matched = re.search(regex, temp_text)
        return result

    def person_name_checker(self, text: str) -> list[Entity]:
        result = []
        doc = self.nlp(text)
        for ent in doc.ents:
            result.append(
                Entity(
                    name=ent.label_,
                    value=ent.text,
                    start=ent.start_char,
                    end=ent.end_char
                )
            )
        return result

    def recognize(self, text: str) -> list[Entity]:
        result = []
        if self.entities.get("person_id"):
            result.extend(self.person_id_checker(text))
        if self.entities.get("email"):
            result.extend(self.email_checker(text))
        if self.entities.get("person_name"):
            result.extend(self.person_name_checker(text))
        result = sorted(result, key=lambda item: item.start, reverse=True)
        return result

    def mask(self, text: str) -> str:
        entities = self.recognize(text)
        for entity in entities:
            text = text[:entity.start] + f"<{entity.name}>" + text[entity.end:]
        return text

    def validate(self, text: str) -> dict[str, str | bool | int]:
        result = self.recognize(text)
        return {
            "raw": text,
            "mask": self.mask(text),
            "validate": len(result) == 0,
            "entities": result
        }
