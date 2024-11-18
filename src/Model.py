import spacy
import spacy.training
import spacy.util
import os
import os.path
import json
import pydantic
import random
import functools
from typing import Any
from src.Doc import Doc


class Model(pydantic.BaseModel):
    name: str
    base_model: str = "pt_core_news_md"
    cache_path: str = os.path.join(os.path.dirname(__file__), ".cache")
    path: str | None = None
    nlp: spacy.Language | None = None
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, __context: Any) -> None:
        if not self.path:
            self.path = f"models/{self.name}"
        print("opa")
        self.load_model()

    def load_model(self) -> spacy.Language:
        try:
            self.nlp = spacy.load(self.path)
        except OSError:
            self.nlp = spacy.blank("pt")
        return self.nlp

    def is_blank(self) -> bool:
        if "ner" in self.nlp.pipe_names:
            ner = self.nlp.get_pipe("ner")
            return len(ner.labels) == 0
        return True

    def create_ner(self, labels: list[str] = []) -> None:
        if "ner" in self.nlp.pipe_names:
            ner = self.nlp.get_pipe("ner")
        else:
            ner = self.nlp.add_pipe("ner")
        for label in labels:
            ner.add_label(label)

    def load_base_model(self) -> None:
        os.makedirs(self.cache_path, exist_ok=True)
        try:
            self.nlp = spacy.load(os.path.join(self.cache_path, self.base_model))
        except Exception:
            spacy.cli.download(self.base_model, False, False, "--no-cache-dir")
            self.nlp = spacy.load(self.base_model)
            self.nlp.to_disk(os.path.join(self.cache_path, self.base_model))

    def load_dataset(self, dataset_path: str) -> list[Doc]:
        print(f"Carregando dataset {dataset_path}")
        file = open(dataset_path)
        json_data = json.load(file)
        return [Doc(text=text) for text in json_data]

    def train(self, datasets: list[list[Doc]], iterations: int = 50) -> None:
        print("Iniciando treinamento...")
        dataset = self.flatten_lists(datasets)
        self.create_ner(labels=["PERSON", "CPF", "CNPJ"])
        self.nlp.begin_training()
        optimizer = self.nlp.create_optimizer()
        losses = {}
        for it in range(iterations):
            random.shuffle(dataset)
            losses = {}
            batches = spacy.util.minibatch(dataset, size=spacy.util.compounding(4, 32, 1.001))
            for batch in batches:
                for doc in batch:
                    nlp_doc = self.nlp.make_doc(doc.text)
                    entities = [
                        (entity.start, entity.end, entity.name)
                        for entity in doc.entities
                    ]
                    example = spacy.training.Example.from_dict(nlp_doc, {"entities": entities})
                    self.nlp.update([example], drop=0.5, sgd=optimizer, losses=losses)
            print(f"Iteração {it + 1}/{iterations}, Perda: {losses['ner']:.3f}")
        self.nlp.to_disk(self.path)

    @staticmethod
    def flatten_lists(lists: list[list[Any]]):
        if any(isinstance(el, list) for el in lists):
            return list(functools.reduce(lambda x, y: x + y, lists, []))
        return lists
