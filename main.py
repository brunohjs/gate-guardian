from dotenv import load_dotenv
from src.PIIDetector import PIIDetector

load_dotenv()

pii = PIIDetector(name="pii_model")
print(pii.mask("Eu quero mascarar meu nome: Bruno"))
